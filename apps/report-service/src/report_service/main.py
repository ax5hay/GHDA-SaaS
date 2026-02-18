"""Report Service - Handles report retrieval, management, and export."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date
from typing import Optional, List
import io

from ghda_db import get_db_session, engine, Base
from ghda_db.models import Report, Document, Facility, Finding, Rule

SERVICE_NAME = "report-service"
PORT = int(os.getenv("REPORT_SERVICE_PORT", "8002"))

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

@app.get("/api/v1/reports")
async def list_reports(
    tenant_id: int = Query(..., description="Tenant ID"),
    facility_id: Optional[int] = Query(None, description="Filter by facility"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    """List reports with optional filters."""
    try:
        query = select(Report).where(Report.tenant_id == tenant_id)
        
        if facility_id:
            query = query.where(Report.facility_id == facility_id)
        if start_date:
            query = query.where(Report.clinic_date >= start_date)
        if end_date:
            query = query.where(Report.clinic_date <= end_date)
        
        query = query.order_by(Report.clinic_date.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Get facility names
        facility_ids = {r.facility_id for r in reports}
        if facility_ids:
            facility_result = await db.execute(
                select(Facility).where(Facility.id.in_(facility_ids))
            )
            facilities = {f.id: f for f in facility_result.scalars().all()}
        else:
            facilities = {}
        
        return {
            "reports": [
                {
                    "id": r.id,
                    "document_id": r.document_id,
                    "facility_id": r.facility_id,
                    "facility_name": facilities.get(r.facility_id, {}).name if facilities.get(r.facility_id) else None,
                    "clinic_date": r.clinic_date.isoformat(),
                    "schema_version": r.schema_version,
                    "quality_indicators": r.quality_indicators,
                    "created_at": r.created_at.isoformat(),
                }
                for r in reports
            ],
            "total": len(reports),
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific report with full data."""
    try:
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Get facility
        facility_result = await db.execute(
            select(Facility).where(Facility.id == report.facility_id)
        )
        facility = facility_result.scalar_one_or_none()
        
        # Get findings
        findings_result = await db.execute(
            select(Finding).where(Finding.report_id == report_id)
        )
        findings = findings_result.scalars().all()
        
        # Get rules for findings
        rule_ids = {f.rule_id for f in findings}
        rules = {}
        if rule_ids:
            rule_result = await db.execute(
                select(Rule).where(Rule.id.in_(rule_ids))
            )
            rules = {r.id: r for r in rule_result.scalars().all()}
        
        return {
            "id": report.id,
            "document_id": report.document_id,
            "facility": {
                "id": facility.id if facility else None,
                "name": facility.name if facility else None,
                "type": facility.type if facility else None,
                "district": facility.district if facility else None,
            } if facility else None,
            "clinic_date": report.clinic_date.isoformat(),
            "schema_version": report.schema_version,
            "data": report.data,
            "quality_indicators": report.quality_indicators,
            "findings": [
                {
                    "id": f.id,
                    "rule": {
                        "rule_id": rules.get(f.rule_id, {}).rule_id if rules.get(f.rule_id) else None,
                        "name": rules.get(f.rule_id, {}).name if rules.get(f.rule_id) else None,
                        "category": rules.get(f.rule_id, {}).category if rules.get(f.rule_id) else None,
                    } if rules.get(f.rule_id) else None,
                    "severity": f.severity,
                    "flag": f.flag,
                    "message": f.message,
                    "evidence": f.evidence,
                }
                for f in findings
            ],
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/{report_id}/findings")
async def get_report_findings(
    report_id: int,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get findings for a specific report."""
    try:
        # Verify report exists
        report_result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = report_result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        query = select(Finding).where(Finding.report_id == report_id)
        if severity:
            query = query.where(Finding.severity == severity)
        
        result = await db.execute(query)
        findings = result.scalars().all()
        
        # Get rules
        rule_ids = {f.rule_id for f in findings}
        rules = {}
        if rule_ids:
            rule_result = await db.execute(
                select(Rule).where(Rule.id.in_(rule_ids))
            )
            rules = {r.id: r for r in rule_result.scalars().all()}
        
        return {
            "report_id": report_id,
            "findings": [
                {
                    "id": f.id,
                    "rule_id": rules.get(f.rule_id, {}).rule_id if rules.get(f.rule_id) else None,
                    "rule_name": rules.get(f.rule_id, {}).name if rules.get(f.rule_id) else None,
                    "category": rules.get(f.rule_id, {}).category if rules.get(f.rule_id) else None,
                    "severity": f.severity,
                    "flag": f.flag,
                    "message": f.message,
                    "evidence": f.evidence,
                }
                for f in findings
            ],
            "total": len(findings),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting findings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/{report_id}/export/pdf")
async def export_report_pdf(
    report_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Export report as PDF."""
    try:
        # Get report data
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # TODO: Implement PDF generation using reportlab
        # For now, return JSON
        return JSONResponse(
            status_code=501,
            content={"message": "PDF export not yet implemented"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/{report_id}/export/excel")
async def export_report_excel(
    report_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Export report as Excel."""
    try:
        # Get report data
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # TODO: Implement Excel generation using openpyxl
        # For now, return JSON
        return JSONResponse(
            status_code=501,
            content={"message": "Excel export not yet implemented"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
