# Document Query API

A FastAPI-based service that processes PDF documents and answers questions using Large Language Models (LLMs) with vector search capabilities.

## Features

- **PDF Processing**: Downloads and extracts text from PDF documents
- **Vector Search**: Uses FAISS for efficient similarity search with sentence embeddings
- **Recursive Text Chunking**: Intelligently splits documents into manageable chunks
- **LLM Integration**: Uses OpenAI's GPT models for question answering
- **Async Processing**: Handles long-running queries with background tasks
- **Answer Validation**: Validates that answers properly address the query (Enhancement 1)
- **RESTful API**: Clean API design with proper error handling

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI     │────▶│ Background  │
└─────────────┘     │  Endpoints   │     │   Tasks     │
                    └──────────────┘     └─────────────┘
                            │                     │
                    ┌───────▼─────────┐  ┌───────▼────────┐
                    │ Query Processor │  │ PDF Processor  │
                    └─────────────────┘  └────────────────┘
                            │                     │
                    ┌───────▼─────────┐  ┌───────▼────────┐
                    │  Text Chunker   │  │ Vector Store   │
                    └─────────────────┘  │    (FAISS)     │
                            │            └────────────────┘
                    ┌───────▼─────────┐
                    │   LLM Service   │
                    │    (OpenAI)     │
                    └─────────────────┘
```

## Prerequisites

- Docker
- OpenAI API Key

## Setup Instructions

1. **Clone the repository** (if applicable)

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Build and run with Docker**:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   The API will be available at `http://localhost:8080`

## API Endpoints

### 1. Query Documents (Async)
**POST** `/query`

Processes a query against provided documents asynchronously.

Request:
```json
{
  "query": "is the home roof age compliant with the underwriting guide rules?",
  "document_urls": [
    "https://example.com/document1.pdf",
    "https://example.com/document2.pdf"
  ]
}
```

Response:
```json
{
  "answer": "Query is being processed. Use the job_id to check status.",
  "status": "pending",
  "job_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. Check Job Status
**GET** `/jobs/{job_id}`

Check the status of an async query job.

Response (when completed):
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:01:00",
  "result": {
    "answer": "The roof was installed in 2022 and meets the requirements...",
    "confidence_note": "Answer based directly on provided context.",
    "metadata": {
      "chunks_used": 5,
      "total_chunks": 120,
      "documents_processed": 2,
      "model_used": "gpt-3.5-turbo"
    }
  }
}
```

### 3. Query Documents (Sync)
**POST** `/query-sync`

Synchronous endpoint for testing (may timeout for large documents).

### 4. Health Check
**GET** `/health`

Returns the health status of the API.

### 5. API Documentation
**GET** `/docs`

Interactive API documentation (Swagger UI).

## Design Choices

### API Design
- **Async Processing**: Main `/query` endpoint returns immediately with a job ID to handle long-running LLM requests and avoid timeout issues
- **Job Status Endpoint**: Allows clients to poll for results
- **Sync Endpoint**: Provided for testing and small documents
- **RESTful Design**: Clear resource-based URLs with appropriate HTTP methods
- **Pydantic Models**: Strong typing for request/response validation

### Chunking Strategy
- **Recursive Character Text Splitting**: Uses LangChain's RecursiveCharacterTextSplitter
- **Chunk Size**: 500 characters (configurable) - balances context and embedding quality
- **Overlap**: 50 characters - ensures continuity between chunks
- **Separators**: Hierarchical splitting on paragraphs, sentences, then characters

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Rationale**: 
  - Lightweight and fast
  - Good balance of quality vs performance
  - 384-dimensional embeddings
  - Well-suited for semantic search

### Vector Store
- **FAISS**: Facebook AI Similarity Search
- **Index Type**: Flat L2 distance for exact search
- **In-Memory**: For this demo (can be persisted in production)

### LLM Prompt Design
- **System Prompt**: Instructs model to only use provided context
- **Context Format**: Clear source attribution for each chunk
- **Temperature**: 0.1 for consistent, factual responses
- **Validation**: Secondary prompt to verify answer quality (Enhancement 1)

## Limitations

1. **In-Memory Job Storage**: Jobs are lost on restart (use Redis in production)
2. **No Authentication**: Add API keys or OAuth in production
3. **Single Instance**: No horizontal scaling (use Celery + Redis for production)
4. **PDF Only**: Currently only supports PDF documents
5. **Context Window**: Limited by LLM token limits
6. **No Caching**: Reprocesses documents each time

## Production Considerations

### Scaling
1. **Horizontal Scaling**:
   - Use Kubernetes for container orchestration
   - Implement Redis for distributed job queue
   - Use Celery for distributed task processing

2. **Vector Store**:
   - Use persistent storage (PostgreSQL with pgvector or dedicated vector DB)
   - Implement caching for frequently accessed documents
   - Consider approximate nearest neighbor search for large scale

3. **API Gateway**:
   - Add rate limiting
   - Implement authentication/authorization
   - Add request/response logging

### Monitoring
- Add APM (Application Performance Monitoring)
- Implement structured logging
- Set up alerts for failures and slow queries
- Track LLM token usage and costs

### Security
- Validate and sanitize PDF URLs
- Implement file size limits
- Add virus scanning for uploaded files
- Use secrets management for API keys
- Implement HTTPS/TLS

### Performance Optimizations
1. **Caching**:
   - Cache processed documents
   - Cache embeddings
   - Cache LLM responses for identical queries

2. **Batch Processing**:
   - Process multiple documents in parallel
   - Batch embedding generation

3. **Database**:
   - Store processed documents and chunks
   - Implement document versioning
   - Add metadata indexing

## Enhancement 1: Answer Validation

The system includes a validation step that:
- Checks if the answer directly addresses the query
- Verifies the answer is based on provided context
- Adds confidence notes to responses

**Limitations**:
- Adds latency (extra LLM call)
- Validation quality depends on LLM performance

**Optimizations**:
- Use a smaller, faster model for validation
- Implement rule-based validation for common patterns
- Cache validation results

## Enhancement 2: Vector Search Implementation

The system implements full vector search with:
- Document chunking with configurable size and overlap
- Sentence transformer embeddings
- FAISS vector index for similarity search
- Top-K retrieval of relevant chunks

This enhancement is fully integrated into the main solution.

## Testing

Test with the provided example:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "is the home roof age compliant with the underwriting guide rules set in the training guide PDF?",
    "document_urls": [
      "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/wind_inspection_report.pdf",
      "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/Training-Guide-ATG-03052019_PDF.pdf"
    ]
  }'
```

Then check the job status:
```bash
curl http://localhost:8080/jobs/{job_id}
```

## License

This project is created for the freeflow take-home assessment.