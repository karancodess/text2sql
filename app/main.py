"""
Main entry point: FastAPI application for the Text-to-SQL service.
Provides REST API endpoints for interacting with the agentic workflow.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config import settings
from db import init_db
from graph.workflow import Text2SQLWorkflow

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Text-to-SQL Agent",
    description="Production-ready agentic Text-to-SQL system",
    version="1.0.0",
)

# Add CORS middleware for client communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow
workflow = Text2SQLWorkflow()


class QueryRequest(BaseModel):
    """Request model for text-to-SQL queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for text-to-SQL queries."""
    user_query: str
    plan: Optional[str]
    sql: Optional[str]
    is_valid: bool
    final_answer: str
    execution_results: Optional[dict]
    error: Optional[str]


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Application starting up...")
    init_db()
    logger.info("Database initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a natural language query and return the result.
    
    Args:
        request (QueryRequest): The query request containing the natural language query.
    
    Returns:
        QueryResponse: The complete workflow result.
    
    Raises:
        HTTPException: If the query processing fails.
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Run the workflow
        result = workflow.run(request.query)
        
        # Return response
        return QueryResponse(
            user_query=result.get("user_query"),
            plan=result.get("plan"),
            sql=result.get("sql"),
            is_valid=result.get("is_valid", False),
            final_answer=result.get("final_answer", ""),
            execution_results=result.get("execution_results"),
            error=result.get("error"),
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
async def get_schema():
    """
    Get the database schema information.
    
    Returns:
        dict: The database schema.
    """
    try:
        from tools.db_tools import get_database_schema
        return get_database_schema()
    except Exception as e:
        logger.error(f"Error retrieving schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Text-to-SQL Agent API",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "schema": "/schema",
            "docs": "/docs",
        },
    }


def main():
    """Main entry point."""
    logger.info("Starting Text-to-SQL Agent API")
    
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
