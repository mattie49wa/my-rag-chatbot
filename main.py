from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
import uvicorn
import uuid
from datetime import datetime

from app.services.query_processor import QueryProcessor
from app.core.config import settings

# Create FastAPI instance
app = FastAPI(
    title=settings.api_title,
    description="API for querying documents using LLM",
    version=settings.api_version,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    document_urls: List[HttpUrl]


class QueryResponse(BaseModel):
    answer: str
    confidence_note: Optional[str] = None
    job_id: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[QueryResponse] = None
    error: Optional[str] = None


jobs: Dict[str, Dict] = {}

_query_processor = None


def get_query_processor():
    """Lazy initialization of query processor."""
    global _query_processor
    if _query_processor is None:
        _query_processor = QueryProcessor()
    return _query_processor


async def process_query_background(job_id: str, query: str, document_urls: List[str]):
    try:
        jobs[job_id]["status"] = "processing"

        query_processor = get_query_processor()
        result = await query_processor.process_query(
            query=query,
            document_urls=[str(url) for url in document_urls],
            validate=True,
        )

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["result"] = result

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["error"] = str(e)


@app.get("/")
async def root():
    return {"message": "Document Query API is running"}


@app.get("/hello")
async def hello_world():
    return {"message": "Hello World!"}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "query": request.query,
        "document_urls": [str(url) for url in request.document_urls],
    }

    background_tasks.add_task(
        process_query_background, job_id, request.query, request.document_urls
    )

    return QueryResponse(
        answer="Query is being processed. Use the job_id to check status.",
        status="pending",
        job_id=job_id,
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a query job."""
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    job = jobs[job_id]

    response = JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        error=job.get("error"),
    )

    if job["status"] == "completed" and "result" in job:
        result = job["result"]
        response.result = QueryResponse(
            answer=result["answer"],
            confidence_note=result.get("confidence_note"),
            metadata=result.get("metadata"),
        )

    return response


@app.post("/query-sync", response_model=QueryResponse)
async def query_documents_sync(request: QueryRequest):
    """
    Synchronous endpoint for testing - processes query immediately.
    Note: This may timeout for large documents.
    """
    try:
        query_processor = get_query_processor()
        result = await query_processor.process_query(
            query=request.query,
            document_urls=[str(url) for url in request.document_urls],
            validate=True,
        )

        return QueryResponse(
            answer=result["answer"],
            confidence_note=result.get("confidence_note"),
            status="completed",
            metadata=result.get("metadata"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api_version,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
