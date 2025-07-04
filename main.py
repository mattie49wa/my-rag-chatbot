from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="Document Query API",
    description="API for querying documents using LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Document Query API is running"}

@app.get("/hello")
async def hello_world():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
