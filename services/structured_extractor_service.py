# structured_extractor.py
import json
import logging
from typing import Dict, Optional, Any
import asyncio
import boto3

# Import local modules
import config.config_kb_loan  as config_kb_loan
import api.models.schemas as schemas
from utils.bedrock_kb_retriever import BedrockKnowledgeBaseRetriever
from services.bedrock_llm_generator import BedrockLLMGenerator

# Optional: JSON Schema validation library
try:
    # Use jsonschema for validation if available
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    # Fallback if jsonschema is not installed
    JSONSCHEMA_AVAILABLE = False
    validate = None
    ValidationError = None

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb', region_name=config_kb_loan.AWS_REGION)

class StructuredExtractorService:
    """
    Orchestrates the process of retrieving document context from a Bedrock KB
    and generating structured data using a Bedrock LLM based on a defined schema.

    Handles retrieval, generation parameter overrides, generation invocation,
    output parsing, and optional schema validation.
    """
    def __init__(self):
        """Initializes the retriever and generator components."""
        self.retriever = BedrockKnowledgeBaseRetriever(
            kb_id=config_kb_loan.KB_ID,
            region_name=config_kb_loan.AWS_REGION
        )
        self.generator = BedrockLLMGenerator(
            model_id=config_kb_loan.GENERATION_MODEL_ID,
            region_name=config_kb_loan.AWS_REGION
        )
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema library not found. JSON schema validation will be skipped.")

    def _parse_and_validate(self, raw_output: str, schema: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Attempts to parse the raw model output string as JSON and optionally validate
        it against the provided JSON schema dictionary.

        Args:
            raw_output: The raw string output from the language model.
            schema: The JSON schema dictionary to validate against. If None or if
                    jsonschema is not installed, validation is skipped.

        Returns:
            The parsed dictionary if successful and valid (if validation enabled),
            otherwise None.
        """
        if not raw_output:
            logger.error("Parsing failed: Raw output from model was empty.")
            return None

        logger.debug(f"Attempting to parse raw output (first 200 chars): {raw_output[:200]}...")

        cleaned_output = raw_output.strip()
        # Remove common markdown code fences if present
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        cleaned_output = cleaned_output.strip() # Strip again after removing fences

        # Basic structural check before attempting full JSON parsing
        if not (cleaned_output.startswith('{') and cleaned_output.endswith('}')):
             logger.error(f"Parsing failed: Output does not appear to be a valid JSON object. "
                          f"Starts with: '{cleaned_output[:50]}', ends with: '{cleaned_output[-50:]}'")
             return None

        try:
            structured_data = json.loads(cleaned_output)
            logger.info("Successfully parsed JSON output from model.")

            # --- Optional: JSON Schema Validation ---
            if JSONSCHEMA_AVAILABLE and schema:
                try:
                    validate(instance=structured_data, schema=schema)
                    logger.info("JSON output successfully validated against the provided schema.")
                except ValidationError as ve:
                    # Log detailed validation error
                    path_str = "/".join(map(str, ve.path)) if ve.path else "root"
                    logger.error(f"JSON Schema Validation Failed: {ve.message} (Path: '{path_str}')")
                    # Log the data structure that failed validation for debugging
                    try:
                        invalid_data_str = json.dumps(structured_data, indent=2)
                    except TypeError: # Handle potential non-serializable data in error logging
                        invalid_data_str = str(structured_data)
                    logger.error(f"Invalid Data Structure:\n{invalid_data_str}")
                    return None # Indicate failure due to validation error
            elif not JSONSCHEMA_AVAILABLE:
                 logger.debug("Skipping JSON schema validation (jsonschema library not installed).")
            elif not schema:
                 logger.debug("Skipping JSON schema validation (no schema provided).")

            return structured_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Failed: {e}")
            # Log the cleaned output that failed parsing for easier debugging
            logger.error(f"Cleaned output that failed parsing:\n{cleaned_output}")
            return None
        except Exception as e:
            # Catch any other unexpected errors during parsing or validation
            logger.exception(f"An unexpected error occurred during parsing/validation: {e}")
            return None
    
    def extract_from_document(
        self,
        document_identifier: str,
        schema_name: str,
        retrieval_query: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Performs the end-to-end structured data extraction for a specific document
        identified within the Knowledge Base and saves the result to DynamoDB.

        Args:
            document_identifier: The value identifying the document in KB metadata
                                 (e.g., a custom ID like 'application_id').
            schema_name: The name of the target schema defined in schemas.py
                         (e.g., 'credit_agreement').
            retrieval_query: Optional specific query text for the retrieval step.
                             If None, the retriever might use a default or the identifier.
            temperature: Optional temperature override for the generation step.
            max_tokens: Optional max_tokens override for the generation step.

        Returns:
            A dictionary containing the extracted structured data conforming to the schema,
            or None if any step (schema loading, retrieval, generation, parsing, validation) fails.
        """
        logger.info(f"Starting structured extraction for document identifier: '{document_identifier}', schema: '{schema_name}'")

        # 1. Get the target schema definition from schemas module
        target_schema = schemas.get_schema(schema_name)
        if not target_schema:
            logger.error(f"Extraction failed: Schema '{schema_name}' not found in schemas.py.")
            return None
        logger.debug(f"Successfully retrieved schema definition for '{schema_name}'.")

        # 2. Retrieve relevant context chunks from the Knowledge Base
        logger.debug(f"Retrieving context using identifier '{document_identifier}' and metadata key 'loanBookingId'...")
        context_chunks = self.retriever.retrieve_document_chunks(
            document_identifier=document_identifier,
            metadata_key='loanBookingId',
            query_text=retrieval_query,
            num_results=config_kb_loan.NUMBER_OF_RETRIEVAL_RESULTS
        )
        if not context_chunks:
            logger.error(f"Extraction failed: Could not retrieve context for identifier '{document_identifier}'. "
                         f"Ensure KB sync completed and metadata field 'loanBookingId' "
                         f"with value '{document_identifier}' exists in the indexed document.")
            return None
        logger.info(f"Retrieved {len(context_chunks)} context chunks for identifier '{document_identifier}'.")

        # --- Temporarily override generator parameters if provided ---
        original_temp = self.generator.temperature
        original_max_tokens = self.generator.max_tokens_to_sample
        raw_llm_output = None

        try:
            if temperature is not None:
                self.generator.temperature = temperature
                logger.debug(f"Using temporary temperature override: {temperature}")
            if max_tokens is not None:
                self.generator.max_tokens_to_sample = max_tokens
                logger.debug(f"Using temporary max_tokens override: {max_tokens}")

            # 3. Generate structured data using the LLM with retrieved context and schema
            logger.debug("Invoking LLM generator with retrieved context and target schema...")
            raw_llm_output = self.generator.generate_structured_data(
                context_chunks=context_chunks,
                desired_schema=target_schema
            )
        except Exception as gen_err:
            logger.exception(f"An error occurred during the generation step: {gen_err}")
        finally:
            self.generator.temperature = original_temp
            self.generator.max_tokens_to_sample = original_max_tokens
            logger.debug("Restored original generator parameters (temperature, max_tokens).")

        if not raw_llm_output:
            logger.error(f"Extraction failed: Generation step did not produce output for identifier '{document_identifier}'.")
            return None
        logger.info(f"LLM generation completed for identifier '{document_identifier}'.")

        # 4. Parse and Validate the raw LLM output against the schema
        logger.debug("Parsing and validating the generated output...")
        structured_data = self._parse_and_validate(raw_llm_output, target_schema)

        if not structured_data:
            logger.error(f"Extraction failed: Could not parse or validate LLM output for identifier '{document_identifier}'.")
            return None


        # 5. Save to DynamoDB (DISABLED FOR NOW)
        # try:
        #     logger.info(f"Saving extracted data to DynamoDB table: '{config_kb_loan.LOAN_BOOKING_TABLE_NAME}'")
        #     self.save_json_to_dynamodb(
        #         table_name=config_kb_loan.LOAN_BOOKING_TABLE_NAME,
        #         loan_booking_id=document_identifier,
        #         extracted_data=structured_data,
        #         timestamp=None  # Pass a valid timestamp or None if it should be retrieved dynamically
        #     )
        # except Exception as e:
        #     logger.error(f"Failed to save extracted data to DynamoDB: {e}")
        #     return None

        logger.info(f"Successfully extracted and saved structured data for document identifier: '{document_identifier}'")
        
        # Return in the format expected by the API
        return {
            "document_identifier": document_identifier,
            "schema_used": schema_name,
            "extracted_data": structured_data,
            "extraction_status": "success"
        }

    def save_json_to_dynamodb(self, table_name: str, loan_booking_id: str, extracted_data: dict, timestamp: Optional[int] = None):
        """
        Save the extracted JSON data to the specified DynamoDB table.

        Args:
            table_name (str): The name of the DynamoDB table.
            loan_booking_id (str): The partition key of the item in the DynamoDB table.
            extracted_data (dict): The extracted data to be added as a new attribute.
            timestamp (Optional[int]): The sort key of the item in the DynamoDB table (if applicable).
        """
        try:
            logger.info(f"Saving extracted data to DynamoDB table: {table_name}")
            
            if timestamp is None:
                # Query the table to retrieve the timestamp (sort key)
                response = dynamodb_client.query(
                    TableName=table_name,
                    KeyConditionExpression="loanBookingId = :loanBookingId",
                    ExpressionAttributeValues={":loanBookingId": {"S": loan_booking_id}}
                )
                items = response.get("Items", [])
                if not items:
                    logger.error(f"No items found for loanBookingId: {loan_booking_id}")
                    raise ValueError(f"Item with loanBookingId {loan_booking_id} does not exist.")
                timestamp = int(items[0]["timestamp"]["N"])  # Retrieve the numeric sort key

            # Prepare the update expression and attribute values
            update_expression = "SET extractedData = :extractedData"
            expression_attribute_values = {
                ":extractedData": {"S": json.dumps(extracted_data) if extracted_data else "{}"}
            }
            
            # Update the item in DynamoDB
            dynamodb_client.update_item(
                TableName=table_name,
                Key={
                    "loanBookingId": {"S": loan_booking_id},
                    "timestamp": {"N": str(timestamp)}  # Sort key as a number
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            logger.info(f"Successfully saved extracted data for loan_booking_id: {loan_booking_id}, timestamp: {timestamp}")
        except Exception as e:
            logger.error(f"Failed to save extracted data to DynamoDB: {e}")
            raise

class StructuredExtractorServiceAsync:
    """
    Async version of the structured extractor service.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def async_extract(
        self,
        loan_booking_id: str,
        product_name: str,
        customer_name: str,
        schema_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously extract structured data from documents associated with a loan booking.
        
        Args:
            loan_booking_id: Loan booking identifier
            product_name: Product name
            customer_name: Customer name
            schema_name: Schema to use for extraction
            
        Returns:
            Extracted data dictionary or None if extraction fails
        """
        try:
            self.logger.info(f"Starting async extraction for loan booking: {loan_booking_id}")
            
            # This is a placeholder implementation
            # You'll need to implement the actual async extraction logic
            
            result = {
                "loan_booking_id": loan_booking_id,
                "product_name": product_name,
                "customer_name": customer_name,
                "schema_used": schema_name,
                "extraction_status": "placeholder_implementation",
                "message": "Async extraction service needs to be implemented"
            }
            
            self.logger.info(f"Async extraction completed for loan booking: {loan_booking_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during async extraction: {str(e)}")
            return None
