from typing import Generator

import pytest

from dynarag import DynaRAGClient


@pytest.fixture
def client() -> DynaRAGClient:
    """Create a DynaRAG client instance."""
    return DynaRAGClient()


@pytest.fixture
def sample_chunk() -> Generator[None, None, None]:
    """Add and cleanup a sample chunk."""
    client = DynaRAGClient()
    chunk_text = "This is a test chunk for the DynaRAG API client test suite."
    filepath = "test_file.txt"

    # Add the chunk
    client.add_chunk(chunk_text, filepath)

    yield

    # Cleanup after tests
    client.delete_chunks(dry_run=False)


def test_add_chunk(client: DynaRAGClient) -> None:
    """Test adding a chunk."""
    chunk_text = "Test chunk content"
    filepath = "test.txt"

    # Should not raise any exceptions
    client.add_chunk(chunk_text, filepath)


def test_similar_with_chunks(client: DynaRAGClient, sample_chunk: None) -> None:
    """Test similar endpoint with existing chunks."""
    similar_chunks = client.similar("test chunk")
    assert similar_chunks is not None
    assert len(similar_chunks) > 0

    # Validate chunk structure
    chunk = similar_chunks[0]
    assert isinstance(chunk["ID"], int)
    assert isinstance(chunk["DocumentID"], int)
    assert isinstance(chunk["ChunkText"], str)
    assert isinstance(chunk["ChunkSize"], int)
    assert isinstance(chunk["FilePath"], str)
    assert isinstance(chunk["Distance"], float)
    assert isinstance(chunk["Similarity"], float)


def test_similar_without_chunks(client: DynaRAGClient) -> None:
    """Test similar endpoint with no chunks."""
    # First ensure no chunks exist
    client.delete_chunks(dry_run=False)

    similar_chunks = client.similar("test query")
    assert similar_chunks is None


def test_query_with_chunks(client: DynaRAGClient, sample_chunk: None) -> None:
    """Test query endpoint with existing chunks."""
    response = client.query("What is this about?")
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


# TODO: Update once model is fixed.
# def test_query_without_chunks(client: DynaRAGClient) -> None:
#     """Test query endpoint with no chunks."""
#     # First ensure no chunks exist
#     client.delete_chunks(dry_run=False)

#     with pytest.raises(BadAPIRequest):
#         client.query("What is this about?")


def test_delete_chunks(client: DynaRAGClient, sample_chunk: None) -> None:
    """Test deleting chunks."""
    # First test dry run
    stats = client.delete_chunks(dry_run=True)
    assert stats["EmbeddingCount"] > 0
    assert stats["DocumentCount"] > 0
    assert len(stats["FilePaths"]) > 0

    # Then actual deletion
    stats = client.delete_chunks(dry_run=False)
    assert stats["EmbeddingCount"] > 0
    assert stats["DocumentCount"] > 0
    assert len(stats["FilePaths"]) > 0

    # Verify deletion
    chunks = client.list_chunks()
    assert chunks is None


def test_get_stats_with_chunks(client: DynaRAGClient, sample_chunk: None) -> None:
    """Test getting stats with existing chunks."""
    stats = client.get_stats()
    assert stats["total_bytes"] > 0
    assert stats["api_requests"] > 0
    assert stats["document_count"] > 0
    assert stats["chunk_count"] > 0


def test_get_stats_without_chunks(client: DynaRAGClient) -> None:
    """Test getting stats with no chunks."""
    # First ensure no chunks exist
    client.delete_chunks(dry_run=False)

    stats = client.get_stats()
    assert stats["document_count"] == 0
    assert stats["chunk_count"] == 0


def test_list_chunks_with_chunks(client: DynaRAGClient, sample_chunk: None) -> None:
    """Test listing chunks with existing chunks."""
    chunks = client.list_chunks()
    assert chunks is not None
    assert len(chunks) > 0

    # Validate chunk structure
    chunk = chunks[0]
    assert isinstance(chunk["ID"], int)
    assert isinstance(chunk["ChunkText"], str)
    assert isinstance(chunk["ChunkSize"], int)
    assert isinstance(chunk["ModelName"], str)
    assert isinstance(chunk["CreatedAt"], str)
    assert isinstance(chunk["FilePath"], str)
    assert isinstance(chunk["DocumentID"], int)


def test_list_chunks_without_chunks(client: DynaRAGClient) -> None:
    """Test listing chunks with no chunks."""
    # First ensure no chunks exist
    client.delete_chunks(dry_run=False)

    chunks = client.list_chunks()
    assert chunks is None
