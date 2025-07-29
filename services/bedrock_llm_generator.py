# bedrock_llm_generator.py
import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import List, Dict, Optional, Any

import config.config_kb_loan as config_kb_loan

logger = logging.getLogger(__name__)

class BedrockLLMGenerator:
    """
    Handles invoking a Bedrock foundation model (like Claude 3.5 Sonnet)
    to generate structured JSON output based on provided context and a target schema.
    """
    def __init__(self, model_id: str, region_name: str):
        """
        Initializes the generator with model details and Bedrock client.

        Args:
            model_id: The Bedrock model ID (e.g., 'anthropic.claude-3-5-sonnet-20240620-v1:0').
            region_name: The AWS region where the model is available.
        """
        if not model_id:
            raise ValueError("Generation Model ID (GENERATION_MODEL_ID) is not configured properly.")
        self.model_id = model_id
        self.region_name = region_name

        # --- Default Generation Parameters (can be overridden per request) ---
        # Initialize with None, allowing model defaults unless explicitly set
        self.temperature: Optional[float] = None
        # Default max tokens from config, can be overridden
        self.max_tokens_to_sample: int = getattr(config_kb_loan, 'MAX_TOKENS_TO_SAMPLE', 4000)

        try:
            # Use bedrock-runtime client for model invocation
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.region_name
            )
            logger.info(f"Bedrock Runtime client initialized for region {region_name}")
        except Exception as e:
            logger.exception("Failed to initialize Bedrock Runtime client.")
            raise

    def _construct_prompt(self, context_chunks: List[Dict], desired_schema: Dict) -> Optional[str]:
        """
        Creates the detailed prompt for the LLM, including context and schema instructions.

        Args:
            context_chunks: List of dictionaries, where each dict represents a retrieved
                            chunk containing at least {'content': {'text': '...'}}.
            desired_schema: The dictionary representing the target JSON schema definition.

        Returns:
            The formatted prompt string, or None if context is missing or schema serialization fails.
        """
        if not context_chunks:
            logger.warning("Cannot construct prompt: No context chunks provided.")
            return None

        # Concatenate text content from chunks, separated for clarity
        context_text = "\n\n---\n\n".join([
            chunk.get('content', {}).get('text', '')
            for chunk in context_chunks if chunk.get('content', {}).get('text') # Ensure text exists
        ]).strip()

        if not context_text:
            logger.warning("Cannot construct prompt: Context chunks contained no usable text.")
            return None

        try:
            # Serialize the schema definition into a readable JSON string for the prompt
            schema_description = json.dumps(desired_schema, indent=2)
        except TypeError as e:
            logger.error(f"Failed to serialize the desired schema to JSON: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error serializing schema: {e}")
            return None

        # --- Prompt Engineering - Tailored for Claude 3.5 Sonnet ---
        # This prompt structure guides the model effectively for JSON extraction based on schema.
        prompt = f"""Human: You are an expert data extraction system. Your task is to analyze the provided text context, which comes from a single document identified by its ID, and extract information precisely according to the requested JSON schema.

<document_context>
{context_text}
</document_context>

Strictly adhere to the following instructions for your response:
1.  Extract information *only* from the text provided in `<document_context>`. Do not infer, guess, or add information not explicitly present in the text.
2.  Your *entire* response must be a single, valid JSON object.
3.  The JSON object must conform *exactly* to the structure and data types defined in the `<json_schema>` below. Ensure all required fields specified in the schema are present in your JSON output.
4.  If a specific piece of information required by the schema is not found in the context, use the JSON value `null` for that field's value. Do *not* omit the field itself if it's defined in the schema properties.
5.  Pay close attention to data types specified in the schema (string, number, integer, boolean, array, object) and format the extracted values accordingly. For fields specified as `number` or `integer`, provide only the numeric value without currency symbols, commas, or units, if possible based on the text. For dates (type `string`), use YYYY-MM-DD format if the text allows, otherwise use the format present in the text.
6.  Do not include *any* text, explanations, apologies, or introductory phrases before or after the JSON object. Your response must start *immediately* with `{{` and end *exactly* with `}}`. Do not wrap the JSON in markdown code fences (```json ... ```).

<json_schema>
{schema_description}
</json_schema>

Based *only* on the provided `<document_context>` and adhering strictly to all instructions above, generate the JSON object conforming to the `<json_schema>`."""

        logger.debug(f"Constructed prompt for model {self.model_id}. Prompt length (approx): {len(prompt)} chars.")
        return prompt

    def generate_structured_data(self, context_chunks: List[Dict], desired_schema: Dict) -> Optional[str]:
        """
        Invokes the configured Bedrock model with the constructed prompt to generate structured JSON.

        Args:
            context_chunks: The list of retrieved context chunks from the knowledge base.
            desired_schema: The dictionary representing the target JSON schema definition.

        Returns:
            The raw string output from the model, expected to be a valid JSON string
            conforming to the schema, or None if prompt construction or model invocation fails.
        """
        prompt = self._construct_prompt(context_chunks, desired_schema)
        if not prompt:
            logger.error("Generation failed: Could not construct prompt.")
            return None

        logger.info(f"Invoking model '{self.model_id}' for structured data generation.")

        try:
            # --- Model Invocation Body (Claude 3.5 Sonnet specific) ---
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens_to_sample,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Add temperature if it has been set (override model default)
            if self.temperature is not None:
                request_body["temperature"] = self.temperature
                logger.debug(f"Using temperature: {self.temperature}")

            # Convert the request body dictionary to a JSON string
            body_bytes = json.dumps(request_body).encode('utf-8')

            # Invoke the model via the Bedrock Runtime client
            response = self.client.invoke_model(
                body=body_bytes,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )

            # Read and parse the response body
            response_body_bytes = response.get('body').read()
            response_body = json.loads(response_body_bytes.decode('utf-8'))

            # --- Response Parsing (Claude 3.5 Sonnet specific) ---
            if response_body.get("content") and isinstance(response_body["content"], list) and len(response_body["content"]) > 0:
                 generated_text = response_body["content"][0].get("text", "")
                 if generated_text:
                      logger.info(f"Successfully received generation response from model '{self.model_id}'. Output length: {len(generated_text)} chars.")
                      return generated_text.strip()
                 else:
                      logger.error(f"Model '{self.model_id}' response content block is empty: {response_body}")
                      return None
            else:
                 logger.error(f"Unexpected response structure from model '{self.model_id}': {response_body}")
                 return None

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ClientError invoking model '{self.model_id}': {error_code} - {error_message}")
            return None
        except json.JSONDecodeError as json_err:
             logger.error(f"Failed to decode JSON response from model '{self.model_id}': {json_err}")
             try:
                  raw_response_str = response_body_bytes.decode('utf-8', errors='ignore')
                  logger.error(f"Raw response body that failed decoding:\n{raw_response_str[:500]}...")
             except NameError:
                  pass
             return None
        except Exception as e:
            logger.exception(f"Unexpected error during model invocation or response processing: {e}")
            return None
