# bedrock_kb_retriever.py
import boto3
import logging
from botocore.exceptions import ClientError
from typing import List, Dict, Optional

import config.config_kb_loan

logger = logging.getLogger(__name__)
# Logging setup should ideally be done once in the main application entry point

class BedrockKnowledgeBaseRetriever:
    """
    Handles retrieving relevant text chunks from an Amazon Bedrock Knowledge Base
    based on a document identifier and metadata filtering.
    """
    def __init__(self, kb_id: str, region_name: str):
        """
        Initializes the retriever.

        Args:
            kb_id: The ID of the Bedrock Knowledge Base.
            region_name: The AWS region where the Knowledge Base is located.
        """
        if not kb_id:
            raise ValueError("Knowledge Base ID (KB_ID) is not configured.")
        self.kb_id = kb_id
        self.region_name = region_name
        try:
            # Use bedrock-agent-runtime for retrieve and retrieveAndGenerate APIs
            self.client = boto3.client(
                'bedrock-agent-runtime',
                region_name=self.region_name
            )
            logger.info(f"Bedrock Agent Runtime client initialized for region {region_name}")
        except Exception as e:
            logger.exception("Failed to initialize Bedrock Agent Runtime client.")
            # Depending on the application structure, you might want to raise the exception
            # to prevent the application from starting in a broken state.
            raise

    def retrieve_document_chunks(
        self,
        document_identifier: str,
        metadata_key: str,
        query_text: Optional[str] = None,
        num_results: int = 5
    ) -> Optional[List[Dict]]:
        if not document_identifier:
            logger.error("Retrieval failed: Document identifier is missing.")
            return None
        if not metadata_key:
            logger.error("Retrieval failed: Metadata key for filtering is missing.")
            return None

        # Inline validation logic
        try:
            retrieval_config = {
                'vectorSearchConfiguration': {
                    'numberOfResults': 1,
                    'filter': {
                        'equals': {
                            'key': metadata_key,
                            'value': document_identifier
                        }
                    }
                }
            }

            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalConfiguration=retrieval_config,
                retrievalQuery={
                    'text': f"Validate document with ID {document_identifier}"
                }
            )

            results = response.get('retrievalResults', [])
            if not results:
                logger.warning(f"Document '{document_identifier}' not found in KB '{self.kb_id}'.")
                return None

        except Exception as e:
            logger.exception(f"Error during document validation: {e}")
            return None

        # Use the document identifier itself as the query if no specific query text is provided
        effective_query = query_text if query_text else f"Information related to document ID {document_identifier}"
        logger.info(f"Retrieving chunks for KB '{self.kb_id}' using identifier '{document_identifier}' "
                    f"(metadata key: '{metadata_key}'). Query: '{effective_query[:100]}...'")

        try:
            retrieval_config = {
                'vectorSearchConfiguration': {
                    'numberOfResults': num_results,
                    'filter': {
                        'equals': {
                            'key': metadata_key,
                            'value': document_identifier
                        }
                    }
                }
            }

            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalConfiguration=retrieval_config,
                retrievalQuery={
                    'text': effective_query
                }
            )

            results = response.get('retrievalResults', [])
            if not results:
                logger.warning(f"No chunks retrieved from KB '{self.kb_id}' for identifier '{document_identifier}' "
                               f"with metadata key '{metadata_key}'. Check if the document is indexed correctly "
                               f"and the metadata mapping/value are accurate.")
                return None

            logger.info(f"Successfully retrieved {len(results)} chunks for identifier '{document_identifier}'.")
            return results

        except ClientError as e:
            logger.error(f"AWS ClientError during retrieval from KB '{self.kb_id}': {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error during retrieval from KB '{self.kb_id}': {e}")
            return None
