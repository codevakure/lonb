"""
Field-Level Extractor Service

Enhanced extraction service that provides field-level citations by mapping 
each extracted field to its source document chunks.
"""

import json
import logging
from typing import Dict, Optional, Any, List
import boto3

# Import local modules
import config.config_kb_loan as config_kb_loan
import api.models.schemas as schemas
from utils.bedrock_kb_retriever import BedrockKnowledgeBaseRetriever
from services.bedrock_llm_generator import BedrockLLMGenerator

logger = logging.getLogger(__name__)

class FieldLevelExtractorService:
    """
    Enhanced extractor that provides field-level citations by analyzing which
    document chunks contribute to each extracted field.
    """
    
    def __init__(self):
        """Initialize the retriever and generator components."""
        self.retriever = BedrockKnowledgeBaseRetriever(
            kb_id=config_kb_loan.KB_ID,
            region_name=config_kb_loan.AWS_REGION
        )
        self.generator = BedrockLLMGenerator(
            model_id=config_kb_loan.GENERATION_MODEL_ID,
            region_name=config_kb_loan.AWS_REGION
        )

    def extract_with_field_citations(
        self,
        document_identifier: str,
        schema_name: str,
        retrieval_query: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Performs extraction with field-level citations by mapping each field
        to the document chunks that were used to extract it.
        
        Args:
            document_identifier: The value identifying the document in KB metadata
            schema_name: The name of the target schema defined in schemas.py
            retrieval_query: Optional specific query text for the retrieval step
            temperature: Optional temperature override for the generation step
            max_tokens: Optional max_tokens override for the generation step
            
        Returns:
            A dictionary containing extracted data and field-level citations
        """
        logger.info(f"Starting field-level extraction for document: '{document_identifier}', schema: '{schema_name}'")

        # 1. Get the target schema definition
        target_schema = schemas.get_schema(schema_name)
        if not target_schema:
            logger.error(f"Schema '{schema_name}' not found")
            return None

        # 2. Retrieve relevant context chunks
        context_chunks = self.retriever.retrieve_document_chunks(
            document_identifier=document_identifier,
            metadata_key='loanBookingId',
            query_text=retrieval_query,
            num_results=config_kb_loan.NUMBER_OF_RETRIEVAL_RESULTS
        )
        
        if not context_chunks:
            logger.error(f"No context chunks retrieved for '{document_identifier}'")
            return None

        # 3. Get schema properties to extract field by field
        schema_properties = target_schema.get('properties', {})
        
        # 4. Extract data with field-level citations
        extracted_data = {}
        field_citations = {}
        
        # Use enhanced prompt for field-level extraction
        enhanced_extraction = self._extract_with_enhanced_prompt(
            context_chunks, target_schema, schema_properties, temperature, max_tokens
        )
        
        if enhanced_extraction:
            extracted_data = enhanced_extraction.get('extracted_data', {})
            field_citations = enhanced_extraction.get('field_citations', {})
        
        return {
            "document_identifier": document_identifier,
            "schema_used": schema_name,
            "extracted_data": extracted_data,
            "extraction_status": "success",
            "citations": context_chunks,  # All chunks used
            "field_citations": field_citations  # Field-specific citations
        }

    def _extract_with_enhanced_prompt(
        self,
        context_chunks: List[Dict],
        target_schema: Dict,
        schema_properties: Dict,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Uses an enhanced prompt that asks the LLM to provide field-level citations
        along with the extracted data.
        """
        
        # Temporarily override generator parameters if provided
        original_temp = self.generator.temperature
        original_max_tokens = self.generator.max_tokens_to_sample
        
        try:
            if temperature is not None:
                self.generator.temperature = temperature
            if max_tokens is not None:
                self.generator.max_tokens_to_sample = max_tokens

            # Create enhanced prompt for field-level extraction
            prompt = self._create_field_citation_prompt(context_chunks, target_schema, schema_properties)
            
            if not prompt:
                return None
                
            # Call the LLM with enhanced prompt
            raw_output = self._call_llm_with_prompt(prompt)
            
            if not raw_output:
                return None
                
            # Parse the enhanced response
            return self._parse_field_citation_response(raw_output, context_chunks)
            
        finally:
            # Restore original parameters
            self.generator.temperature = original_temp
            self.generator.max_tokens_to_sample = original_max_tokens

    def _create_field_citation_prompt(
        self,
        context_chunks: List[Dict],
        target_schema: Dict,
        schema_properties: Dict
    ) -> Optional[str]:
        """
        Creates an enhanced prompt that asks the LLM to provide both extracted data
        and citations for each field.
        """
        
        # Number and concatenate chunks for easy reference
        numbered_chunks = []
        for i, chunk in enumerate(context_chunks):
            chunk_text = chunk.get('content', {}).get('text', '').strip()
            if chunk_text:
                numbered_chunks.append(f"[CHUNK_{i+1}]\n{chunk_text}")
        
        if not numbered_chunks:
            return None
            
        context_text = "\n\n".join(numbered_chunks)
        
        # Create list of fields to extract
        field_descriptions = []
        for field_name, field_def in schema_properties.items():
            description = field_def.get('description', f'The {field_name} field')
            field_type = field_def.get('type', 'string')
            field_descriptions.append(f"- {field_name} ({field_type}): {description}")
        
        fields_list = "\n".join(field_descriptions)
        
        prompt = f"""Human: You are an expert data extraction system. Analyze the provided document chunks and extract specific fields with citations.

<document_chunks>
{context_text}
</document_chunks>

Extract the following fields:
{fields_list}

Your response must be a JSON object with this exact structure:
{{
  "extracted_data": {{
    "field_name": "extracted_value",
    ...
  }},
  "field_citations": {{
    "field_name": ["CHUNK_1", "CHUNK_3"],
    ...
  }}
}}

Instructions:
1. For "extracted_data": Extract each field's value based only on the document chunks
2. For "field_citations": List the chunk numbers (e.g., ["CHUNK_1", "CHUNK_2"]) that contain evidence for each field
3. Use null for fields not found in the documents
4. Only reference chunks that actually contain relevant information for each field
5. Your entire response must be valid JSON starting with {{ and ending with }}
