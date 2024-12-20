import os
import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, List, TypeVar, Optional, TypedDict, cast

from dynarag.constants import DYNARAG_BASE_URL
from dynarag.exceptions import BadAPIRequest, MissingAPIToken

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


class Similar(TypedDict):
    ID: int
    DocumentID: int
    ChunkText: str
    ChunkSize: int
    FilePath: str
    Distance: float
    Similarity: float


class DeleteChunks(TypedDict):
    EmbeddingCount: int
    DocumentCount: int
    TotalBytes: int
    FilePaths: List[str]


class UserStats(TypedDict):
    total_bytes: int
    api_requests: int
    document_count: int
    chunk_count: int


class ListChunks(TypedDict):
    ID: int
    ChunkText: str
    ChunkSize: int
    ModelName: str
    CreatedAt: str
    FilePath: str
    DocumentID: int


class DynaRAGClient:
    def __init__(self) -> None:
        """Initialise the DynaRAG client."""
        api_token = os.environ.get("DYNARAG_API_TOKEN", None)
        if not api_token:
            error_str = (
                "Could not find the `DYNARAG_API_TOKEN` environment variable."
                "You can obtain one by going to https://app.dynarag.com/dashboard/developer and generate a token."
            )
            LOGGER.error(error_str)
            raise MissingAPIToken(error_str)

        LOGGER.info("Obtained DynaRAG API key. Successfully initialised.")

        self.base_url = DYNARAG_BASE_URL
        self.api_token = api_token

    def _make_request(
        self,
        return_model: Optional[type[T]],
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] | None = None,
    ) -> Optional[T]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        request = urllib.request.Request(url, headers=headers, method=method)

        if data:
            request.data = json.dumps(data).encode("utf-8")

        try:
            with urllib.request.urlopen(request) as response:
                response_data = response.read()
                if return_model is None:
                    return None
                if response.headers.get("Content-Type") == "application/json":
                    json_data = json.loads(response_data)
                    return cast(T, json_data)
                return cast(T, response_data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise BadAPIRequest(f"API request failed: {e.code} - {e.reason}")

    def add_chunk(self, chunk: str, filepath: str) -> None:
        """Add a text chunk to the knowledge base.

        Args:
            chunk: The text content to add
            filepath: Source file path or identifier for the chunk
        """
        data = {"chunk": chunk, "filepath": filepath}
        self._make_request(
            return_model=None, endpoint="chunk", method="POST", data=data
        )

    def similar(self, text: str, k: int = 5) -> List[Similar] | None:
        """Find similar chunks to the given text.

        Args:
            text: Text to compare against
            k: Number of similar results to return

        Returns:
            List of similar chunks with their metadata, or `None` if no chunks available
        """
        data = {"text": text, "k": k}
        return self._make_request(
            return_model=List[Similar],
            endpoint="similar",
            method="POST",
            data=data,
        )

    def query(self, query: str) -> str:
        """Query the knowledge base using RAG.

        Args:
            query: The question or query text

        Returns:
            Generated response based on the relevant documents
        """
        data = {"query": query}
        resp = self._make_request(
            return_model=str, endpoint="query", method="POST", data=data
        )

        if resp is None:
            raise BadAPIRequest("Expected return value but none found")
        return resp

    def delete_chunks(self, dry_run: bool = False) -> DeleteChunks:
        """Delete all chunks for the current user.

        Args:
            dry_run: If True, only simulate the deletion

        Returns:
            Deletion statistics
        """
        data = {"dryrun": dry_run}
        resp = self._make_request(
            return_model=DeleteChunks,
            endpoint="chunks",
            method="DELETE",
            data=data,
        )
        if resp is None:
            raise BadAPIRequest("Expected return value but none found")
        return resp

    def get_stats(self) -> UserStats:
        """Get usage statistics for the current user.

        Returns:
            UserStats object containing usage metrics
        """
        resp = self._make_request(
            return_model=UserStats, endpoint="stats", method="GET"
        )
        if resp is None:
            raise BadAPIRequest("Expected return value but none found")
        return resp

    def list_chunks(self) -> List[ListChunks] | None:
        """List all chunks for the current user.

        Returns:
            List of chunks with their metadata, or `None` if no chunks exist.
        """
        return self._make_request(
            return_model=List[ListChunks], endpoint="chunks", method="GET"
        )
