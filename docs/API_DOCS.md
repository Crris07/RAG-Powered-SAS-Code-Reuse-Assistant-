# API Reference

## Base URLs

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/api
```

Start the API:

```powershell
cd "C:\Users\HP\SAS RAG ASSISTANT"
.\.venv\Scripts\activate
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
python -m uvicorn src.api.app:app --reload
```

Interactive documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## GET /health

Returns basic service health.

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "healthy"
}
```

## GET /api/stats

Returns vector database and embedding information.

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/stats
```

Response:

```json
{
  "vector_db_documents": 113,
  "embedding_dimension": 384,
  "status": "healthy"
}
```

## POST /api/retrieve

Retrieves reranked SAS snippets without generating new code.

Example:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/retrieve?query=Create%20ADSL%20with%20safety%20flags&top_k=3"
```

Query parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | string | yes | Natural-language AdAM, TLF, listing, or SAS requirement |
| `top_k` | integer | no | Number of snippets to return. Default is 3 |

Response:

```json
{
  "query": "Create ADSL with safety flags",
  "snippets": [
    {
      "id": "01_adsl_generation_chunk_1",
      "code": "data adsl;\n  set adam.dm;\n  ...",
      "similarity": 0.8662,
      "rerank_score": 4.48,
      "final_score": 6.34,
      "hybrid_score": 0.91,
      "keyword_score": 7.25,
      "retrieval_sources": ["vector", "keyword"],
      "metadata": {
        "code_id": "01_adsl_generation",
        "source_file": "01_adsl_generation.sas",
        "chunk_type": "data_step",
        "start_line": 8,
        "end_line": 31
      }
    }
  ],
  "count": 1,
  "status": "success"
}
```

Score fields:

- `similarity`: vector similarity score from ChromaDB
- `keyword_score`: BM25-style keyword score
- `hybrid_score`: combined retrieval score before reranking
- `rerank_score`: cross-encoder score
- `final_score`: blended score used for final ordering
- `retrieval_sources`: whether the snippet came from vector search, keyword search, or both

## POST /api/generate

Retrieves SAS snippets and generates a SAS code suggestion.

Example:

```powershell
$body = @{
  requirement = "Create ADSL dataset with safety population flags"
  top_k = 3
  temperature = 0.2
  max_tokens = 1024
} | ConvertTo-Json

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/generate" -ContentType "application/json" -Body $body
```

Request body:

```json
{
  "requirement": "Create ADSL dataset with safety population flags",
  "top_k": 3,
  "temperature": 0.2,
  "max_tokens": 1024
}
```

Parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `requirement` | string | yes | Natural-language code requirement |
| `top_k` | integer | no | Number of reranked snippets to use. Default is 3 |
| `temperature` | number | no | Generation temperature for real LLM providers |
| `max_tokens` | integer | no | Maximum generation length for real LLM providers |

Response:

```json
{
  "requirement": "Create ADSL dataset with safety population flags",
  "generated_code": "/* Generated SAS suggestion */\ndata adsl;\n  set adam.dm;\n  saffl = ifc(randfl = 'Y', 'Y', 'N');\nrun;",
  "retrieved_snippets": [
    {
      "id": "01_adsl_generation_chunk_1",
      "code": "data adsl;\n  set adam.dm;\n  ...",
      "similarity": 0.8662,
      "rerank_score": 4.48,
      "final_score": 6.34,
      "hybrid_score": 0.91,
      "keyword_score": 7.25,
      "retrieval_sources": ["vector", "keyword"],
      "metadata": {
        "code_id": "01_adsl_generation",
        "source_file": "01_adsl_generation.sas",
        "chunk_type": "data_step",
        "start_line": 8,
        "end_line": 31
      }
    }
  ],
  "assumptions": [
    "Input domains follow synthetic CDISC-like naming.",
    "Generated SAS should be reviewed before production use."
  ],
  "status": "success"
}
```

## Error Responses

Errors use FastAPI's standard response shape, with additional guidance where available.

Example:

```json
{
  "detail": {
    "message": "Unable to generate SAS code.",
    "hint": "Run ingestion first and confirm the embedding and reranker models are cached locally.",
    "error": "No documents found in vector database."
  }
}
```

Common fixes:

- Run `python -m src.cli.cli ingest --reset`
- Confirm `.venv` is active
- Confirm the embedding model is cached locally
- Confirm the reranker model is cached locally
- Remove offline environment variables if you still need to download models

## Demo Script

```powershell
cd "C:\Users\HP\SAS RAG ASSISTANT"
.\.venv\Scripts\activate
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'

python -m src.cli.cli ingest --reset
python -m uvicorn src.api.app:app --reload
```

Then in another PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/stats
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/retrieve?query=Create%20ADSL%20with%20safety%20flags&top_k=3"

$body = @{
  requirement = "Create adverse event listing by severity and relationship"
  top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Method Post "http://127.0.0.1:8000/api/generate" -ContentType "application/json" -Body $body
```

## Production Notes

Current prototype settings are intentionally open for local development:

- No authentication
- No rate limiting
- Broad local CORS behavior
- Synthetic data only
- Demo generator by default

Production should add authentication, authorization, audit logging, model governance, SAS validation, and restricted access to real study code.

