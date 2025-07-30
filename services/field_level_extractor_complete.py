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

        # 3. Get schema properties
        schema_properties = target_schema.get('properties', {})
        
        # 4. Extract data with field-level citations
        enhanced_extraction = self._extract_with_enhanced_prompt(
            context_chunks, target_schema, schema_properties, temperature, max_tokens
        )
        
        if not enhanced_extraction:
            return None
            
        extracted_data = enhanced_extraction.get('extracted_data', {})
        field_citations = enhanced_extraction.get('field_citations', {})
        
        return {
            "document_identifier": document_identifier,
            "schema_used": schema_name,
            "extracted_data": extracted_data,
            "extraction_status": "success",
            "citations": context_chunks,
            "field_citations": field_citations
        }

    def _extract_with_enhanced_prompt(
        self,
        context_chunks: List[Dict],
        target_schema: Dict,
        schema_properties: Dict,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Uses an enhanced prompt for field-level citations."""
        
        original_temp = self.generator.temperature
        original_max_tokens = self.generator.max_tokens_to_sample
        
        try:
            if temperature is not None:
                self.generator.temperature = temperature
            if max_tokens is not None:
                self.generator.max_tokens_to_sample = max_tokens

            prompt = self._create_field_citation_prompt(context_chunks, schema_properties)
            if not prompt:
                return None
                
            raw_output = self._call_llm_with_prompt(prompt)
            if not raw_output:
                return None
                
            return self._parse_field_citation_response(raw_output, context_chunks)
            
        finally:
            self.generator.temperature = original_temp
            self.generator.max_tokens_to_sample = original_max_tokens

    def _create_field_citation_prompt(
        self,
        context_chunks: List[Dict],
        schema_properties: Dict
    ) -> Optional[str]:
        """Creates an enhanced prompt for field-level extraction."""
        
        # Number chunks for reference
        numbered_chunks = []
        for i, chunk in enumerate(context_chunks):
            chunk_text = chunk.get('content', {}).get('text', '').strip()
            if chunk_text:
                numbered_chunks.append(f"[CHUNK_{i+1}]\\n{chunk_text}")
        
        if not numbered_chunks:
            return None
            
        context_text = "\\n\\n".join(numbered_chunks)
        
        # Create field descriptions
        field_descriptions = []
        for field_name, field_def in schema_properties.items():
            description = field_def.get('description', f'The {field_name} field')
            field_type = field_def.get('type', 'string')
            field_descriptions.append(f"- {field_name} ({field_type}): {description}")
        
        fields_list = "\\n".join(field_descriptions)
        
        return f'''Human: Extract specific fields with citations from document chunks.

<document_chunks>
{context_text}
</document_chunks>

Extract these fields:
{fields_list}

Response format (JSON only):
{{
  "extracted_data": {{"field_name": "value"}},
  "field_citations": {{"field_name": ["CHUNK_1", "CHUNK_2"]}}
}}

Rules:
1. Extract values only from the chunks
2. List chunk numbers that contain evidence for each field
3. Use null for missing fields
4. Only cite relevant chunks
5. Return valid JSON only'''

    def _call_llm_with_prompt(self, prompt: str) -> Optional[str]:
        """Call the LLM with the enhanced prompt."""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.generator.max_tokens_to_sample,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if self.generator.temperature is not None:
                request_body["temperature"] = self.generator.temperature
            
            body_bytes = json.dumps(request_body).encode('utf-8')
            
            response = self.generator.client.invoke_model(
                body=body_bytes,
                modelId=self.generator.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read().decode('utf-8'))
            
            if response_body.get("content") and len(response_body["content"]) > 0:
                return response_body["content"][0].get("text", "").strip()
                
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            
        return None

    def _parse_field_citation_response(
        self,
        raw_output: str,
        context_chunks: List[Dict]
    ) -> Optional[Dict[str, Any]]:
        """Parse the LLM response to extract data and field citations."""
        try:
            # Clean the output
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith("```json"):
                cleaned_output = cleaned_output[7:]
            if cleaned_output.endswith("```"):
                cleaned_output = cleaned_output[:-3]
            cleaned_output = cleaned_output.strip()
            
            # Parse JSON
            parsed_data = json.loads(cleaned_output)
            
            extracted_data = parsed_data.get('extracted_data', {})
            chunk_references = parsed_data.get('field_citations', {})
            
            # Convert chunk references to actual chunk data
            field_citations = {}
            for field_name, chunk_refs in chunk_references.items():
                field_citations[field_name] = []
                
                if isinstance(chunk_refs, list):
                    for chunk_ref in chunk_refs:
                        if isinstance(chunk_ref, str) and chunk_ref.startswith("CHUNK_"):
                            try:
                                chunk_index = int(chunk_ref.split("_")[1]) - 1
                                if 0 <= chunk_index < len(context_chunks):
                                    field_citations[field_name].append(context_chunks[chunk_index])
                            except (ValueError, IndexError):
                                continue
            
            return {
                'extracted_data': extracted_data,
                'field_citations': field_citations
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Raw output: {raw_output}")
            
        except Exception as e:
            logger.error(f"Error parsing field citation response: {e}")
            
        return None
