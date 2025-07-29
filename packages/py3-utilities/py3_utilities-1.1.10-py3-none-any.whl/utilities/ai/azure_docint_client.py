import pickle
import logging
from pathlib import Path

from ..utility_base import UtilityBase
from ..logger import Logger, LogWrapper

from typing import Optional
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError, ServiceRequestError
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import ContentFormat, AnalyzeResult


class DocumentIntelligenceClientError(Exception):
    """Unified custom exception for Azure Document Intelligence Client."""
    pass


class AzureDocumentIntelligenceClient(UtilityBase):
    """A wrapper for interacting with Azure Document Intelligence API."""

    def __init__(
        self, 
        endpoint: str, 
        api_key: str,
        verbose: bool = False,
        logger: Optional[logging.Logger | Logger | LogWrapper] = None,
        log_level: Optional[int] = None
    ):
        """Initialize the AzureDocumentIntelligenceClient.

        Args:
            endpoint (str): Azure Document Intelligence endpoint.
            api_key (str): API key for Azure Document Intelligence.
            verbose (bool, optional): If True, enables verbose logging. Defaults to False.
            logger (Optional[logging.Logger | Logger | LogWrapper], optional): Optional logger instance. Defaults to None.
            log_level (Optional[int], optional): Optional log level. If not provided, INFO level will be used. Defaults to None.

        Raises:
            DocumentIntelligenceClientError: If endpoint or API key is missing.
        """
        super().__init__(verbose, logger, log_level)

        if not endpoint or not api_key:
            raise DocumentIntelligenceClientError("Both endpoint and API key are required.")

        self.endpoint = endpoint
        self.api_key = api_key

        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            headers={"x-ms-useragent": "document-intelligence-wrapper/1.0.0"}
        )

    def _get_cache_path(self, file_path: Path) -> Path:
        """Generate the path to the cached pickle file for a given document.

        Args:
            file_path (Path): The path to the original document.

        Returns:
            Path: The path to the corresponding cache file.
        """
        return file_path.parent / f"docint_{file_path.stem}.pkl"

    def parse_document(self, file_path: str, output_format: ContentFormat = ContentFormat.MARKDOWN) -> str:
        """Parse a document and return the result content, caching the result locally.

        Args:
            file_path (str): Path to the document file.
            output_format (ContentFormat, optional): Desired content format. Defaults to ContentFormat.MARKDOWN.

        Returns:
            str: Parsed document content.

        Raises:
            ValueError: If the file does not exist.
            DocumentIntelligenceClientError: If cached result already exists.
            ClientAuthenticationError: If authentication fails.
            HttpResponseError: For HTTP errors.
            ServiceRequestError: For network/service request failures.
            Exception: For any other unexpected errors.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        cache_path = self._get_cache_path(file_path)

        if cache_path.exists():
            raise DocumentIntelligenceClientError(f"Cached result already exists: {cache_path}. Delete the file to reprocess.")

        try:
            self._log(f"Parsing document `{file_path}`...")

            with file_path.open("rb") as file:
                poller = self.client.begin_analyze_document(
                    model_id="prebuilt-layout",
                    analyze_request=file,
                    content_type="application/octet-stream",
                    output_content_format=output_format
                )
                result: AnalyzeResult = poller.result()

            with cache_path.open("wb") as f:
                pickle.dump(result, f)

            self._log(f"Parsing done, saving result to `{cache_path}`")

            return result.content

        except ClientAuthenticationError as e:
            self._log_exception(f"Client authentication error while parsing `{file_path.name}`: {e}")
            raise
        except HttpResponseError as e:
            self._log_exception(f"HTTP error occurred: `{e.message}` while parsing `{file_path.name}`")
            raise
        except ServiceRequestError as e:
            self._log_exception(f"Network or service request failure while parsing `{file_path.name}`: {e}")
            raise 
        except Exception as e:
            self._log_exception(f"Unexpected error during document parsing `{file_path.name}`: {e}")
            raise
