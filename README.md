# DynaRAG

This is the Python client to [DynaRAG](https://github.com/Predixus/DynaRAG).

DynaRAG provides a simple and fast interface to implement RAG (Retrieval Augemented Generation)
into your application.

## Configuration

DynaRAG requires some environment variables to get started:
- `DYNARAG_API_TOKEN` - a signed JWT that contains data needed by DynaRAG. Follow the spec in the [DynaRAG](https://github.com/Predixus/DynaRAG)
service repo.
- `DYNARAG_BASE_URL` - url to the DynaRAG service. e.g. http://localhost:7890

## Usage

Initialise a DynaRAG client:

```python
from dynarag import DynaRAGClient

client = DynaRAGClient()
```

Send a chunk:

```python
chunk = "DynaRAG is awesome"
filepath = "./dev.noext"
client.add_chunk(chunk=chunk,filepath=filepath)
```

Get stats on user chunks:

```python
client.get_chunks()
# {
#     'total_bytes': 90,
#     'api_requests': 281,
#     'document_count': 1,
#     'chunk_count': 5
# }
```

List chunks:

```python
client.list_chunks()
# [
#     {
#         'ID': 102,
#         'ChunkText':
#         'DynaRAG is awesome',
#         'ChunkSize': 18,
#         'ModelName': 'all-MiniLM-L6-v2',
#         'CreatedAt': '2024-12-20T12:46:47.371629Z',
#         'FilePath': './dev.noext',
#         'DocumentID': 107
#     },
#     ...
# ]
```

Find similar chunks:

```python
client.similar(text="Is DynaRAG awesome?", k=1)

# [
#     {
#         'ID': 102,
#         'ChunkText': 'DynaRAG is awesome',
#         'ChunkSize': 18,
#         'ModelName': 'all-MiniLM-L6-v2',
#         'CreatedAt': '2024-12-20T12:46:47.371629Z',
#         'FilePath': './dev.noext',
#         'DocumentID': 107
#     },
#     ...
# ]

```

Query an LLM:

```python
client.query(query="Why is DynaRAG awesome?")

# The documents do not provide a reason why DynaRAG is awesome, they simply state that [DynaRAG is awesome][#ref-0]. No additional information is given.
#
# Searched Documents:
# ref-0: ./dev.noext
```

Delete all chunks, but dry run:

```python
client.delete(dryrun = True)
# {
#     'EmbeddingCount': 5,
#     'DocumentCount': 1,
#     'TotalBytes': 90,
#     'FilePaths': [
#         './dev.noext'
#     ]
# }
```

Commit to deleting:

```python
client.delete(dryrun = False)
# {
#     'EmbeddingCount': 5,
#     'DocumentCount': 1,
#     'TotalBytes': 90,
#     'FilePaths': [
#         './dev.noext'
#     ]
# }
```
