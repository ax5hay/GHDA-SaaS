"""Document Service - Handles document upload and storage."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from datetime import datetime
import hashlib

from ghda_db import get_db_session, engine, Base
from ghda_db.models import Document, Tenant

SERVICE_NAME = "document-service"
PORT = int(os.getenv("DOCUMENT_SERVICE_PORT", "8001"))

# Shared HTTP client for downstream calls
http_client: httpx.AsyncClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifecycle management."""
    global http_client
    
    logger.info(f"{SERVICE_NAME} starting on port {PORT}")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize shared HTTP client
    http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=8),
    )
    app.state.http_client = http_client
    
    yield
    
    # Cleanup
    if http_client:
        await http_client.aclose()
    logger.info(f"{SERVICE_NAME} shutting down")

app = FastAPI(
    title=f"GHDA-SaaS {SERVICE_NAME}",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "database": "connected" if engine else "disconnected",
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # TODO: Add Prometheus metrics
    return {"status": "ok"}

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: int = None,
    db: AsyncSession = Depends(get_db_session),
):
    """Upload a document for processing."""
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        # Check if document already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Document).where(Document.checksum == checksum)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return JSONResponse(
                status_code=200,
                content={
                    "document_id": existing.id,
                    "filename": existing.filename,
                    "status": existing.status,
                    "message": "Document already exists",
                }
            )
        
        # Store in object storage (MinIO/S3)
        # TODO: Implement actual storage
        storage_path = f"documents/{tenant_id}/{checksum}/{file.filename}"
        
        # Create document record
        document = Document(
            filename=file.filename,
            file_type=file.filename.split(".")[-1].upper(),
            file_size=file_size,
            checksum=checksum,
            storage_path=storage_path,
            status="pending",
            tenant_id=tenant_id or 1,
            metadata={"content_type": file.content_type},
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Trigger processing service
        processing_url = os.getenv("PROCESSING_SERVICE_URL", "http://processing-service:8004")
        if http_client:
            try:
                await http_client.post(
                    f"{processing_url}/api/v1/process",
                    json={"document_id": document.id},
                    timeout=5.0,
                )
            except Exception as e:
                logger.warning(f"Failed to trigger processing: {e}")
        
        return JSONResponse(
            status_code=201,
            content={
                "document_id": document.id,
                "filename": document.filename,
                "file_size": document.file_size,
                "status": document.status,
                "uploaded_at": document.created_at.isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/{document_id}")
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get document metadata."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "created_at": document.created_at.isoformat(),
    }

@app.get("/api/v1/documents/{document_id}/status")
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get document processing status."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document.id,
        "status": document.status,
        "updated_at": document.updated_at.isoformat(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
