"""Processing Service - Handles document processing pipeline."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import json

from ghda_db import get_db_session, engine, Base
from ghda_db.models import Document, Report, Facility, Finding, Rule

SERVICE_NAME = "processing-service"
PORT = int(os.getenv("PROCESSING_SERVICE_PORT", "8004"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Service lifecycle management."""
    logger.info(f"{SERVICE_NAME} starting on port {PORT}")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
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

@app.post("/api/v1/process")
async def process_document(
    request: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db_session),
):
    """Process a document."""
    try:
        document_id = request.get("document_id")
        if not document_id:
            raise HTTPException(status_code=400, detail="document_id is required")
        
        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update status to processing
        document.status = "processing"
        await db.commit()
        
        # TODO: Implement actual processing pipeline:
        # 1. Download document from storage (MinIO/S3)
        # 2. Extract text based on file type (DOCX, PDF, OCR)
        # 3. Parse structure
        # 4. Normalize phrases
        # 5. Convert to canonical JSON schema
        # 6. Evaluate rules
        # 7. Create Report and Findings records
        # 8. Update document status
        
        # For now, create a placeholder report
        # In production, this would parse the actual document
        logger.info(f"Processing document {document_id}")
        
        # Update status to completed (placeholder)
        document.status = "completed"
        await db.commit()
        
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Processing pipeline not yet fully implemented",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        # Update document status to failed
        try:
            if document:
                document.status = "failed"
                await db.commit()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/process/batch")
async def process_batch(
    request: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db_session),
):
    """Process multiple documents."""
    try:
        document_ids = request.get("document_ids", [])
        if not document_ids:
            raise HTTPException(status_code=400, detail="document_ids is required")
        
        results = []
        for document_id in document_ids:
            try:
                # Get document
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                
                if not document:
                    results.append({
                        "document_id": document_id,
                        "status": "error",
                        "message": "Document not found",
                    })
                    continue
                
                # Update status
                document.status = "processing"
                await db.commit()
                
                # TODO: Process document
                logger.info(f"Processing document {document_id}")
                
                document.status = "completed"
                await db.commit()
                
                results.append({
                    "document_id": document_id,
                    "status": "completed",
                })
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {e}")
                results.append({
                    "document_id": document_id,
                    "status": "error",
                    "message": str(e),
                })
        
        return {
            "results": results,
            "total": len(document_ids),
            "completed": len([r for r in results if r["status"] == "completed"]),
            "failed": len([r for r in results if r["status"] == "error"]),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/process/status/{document_id}")
async def get_processing_status(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get processing status for a document."""
    try:
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if report exists
        report_result = await db.execute(
            select(Report).where(Report.document_id == document_id)
        )
        report = report_result.scalar_one_or_none()
        
        return {
            "document_id": document_id,
            "status": document.status,
            "has_report": report is not None,
            "report_id": report.id if report else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
