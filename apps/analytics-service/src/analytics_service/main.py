"""Analytics Service - Handles analytics, trends, and insights."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

from ghda_db import get_db_session, engine, Base
from ghda_db.models import Report, Facility, Finding, Rule

SERVICE_NAME = "analytics-service"
PORT = int(os.getenv("ANALYTICS_SERVICE_PORT", "8003"))

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

@app.get("/api/v1/analytics/overview")
async def get_overview(
    tenant_id: int = Query(..., description="Tenant ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get overview analytics."""
    try:
        query = select(Report).where(Report.tenant_id == tenant_id)
        
        if start_date:
            query = query.where(Report.clinic_date >= start_date)
        if end_date:
            query = query.where(Report.clinic_date <= end_date)
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        if not reports:
            return {
                "total_reports": 0,
                "total_facilities": 0,
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None,
                },
            }
        
        facility_ids = {r.facility_id for r in reports}
        
        # Get findings count
        report_ids = {r.id for r in reports}
        findings_count = 0
        if report_ids:
            findings_result = await db.execute(
                select(func.count(Finding.id)).where(Finding.report_id.in_(report_ids))
            )
            findings_count = findings_result.scalar_one() or 0
        
        return {
            "total_reports": len(reports),
            "total_facilities": len(facility_ids),
            "total_findings": findings_count,
            "date_range": {
                "start": min(r.clinic_date for r in reports).isoformat(),
                "end": max(r.clinic_date for r in reports).isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Error getting overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/facilities/{facility_id}/trends")
async def get_facility_trends(
    facility_id: int,
    tenant_id: int = Query(..., description="Tenant ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get trends for a specific facility."""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = select(Report).where(
            and_(
                Report.facility_id == facility_id,
                Report.tenant_id == tenant_id,
                Report.clinic_date >= start_date,
                Report.clinic_date <= end_date,
            )
        ).order_by(Report.clinic_date)
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Get findings for reports
        report_ids = {r.id for r in reports}
        findings = []
        if report_ids:
            findings_result = await db.execute(
                select(Finding).where(Finding.report_id.in_(report_ids))
            )
            findings = findings_result.scalars().all()
        
        # Group by date
        trends = {}
        for report in reports:
            date_str = report.clinic_date.isoformat()
            if date_str not in trends:
                trends[date_str] = {
                    "date": date_str,
                    "reports_count": 0,
                    "findings_count": 0,
                    "high_severity_findings": 0,
                }
            trends[date_str]["reports_count"] += 1
        
        # Count findings by date
        for finding in findings:
            report = next((r for r in reports if r.id == finding.report_id), None)
            if report:
                date_str = report.clinic_date.isoformat()
                if date_str in trends:
                    trends[date_str]["findings_count"] += 1
                    if finding.severity == "high":
                        trends[date_str]["high_severity_findings"] += 1
        
        return {
            "facility_id": facility_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "trends": list(trends.values()),
        }
    except Exception as e:
        logger.error(f"Error getting facility trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/findings/summary")
async def get_findings_summary(
    tenant_id: int = Query(..., description="Tenant ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get summary of findings by severity and category."""
    try:
        # Get reports
        report_query = select(Report.id).where(Report.tenant_id == tenant_id)
        if start_date:
            report_query = report_query.where(Report.clinic_date >= start_date)
        if end_date:
            report_query = report_query.where(Report.clinic_date <= end_date)
        
        report_result = await db.execute(report_query)
        report_ids = [r[0] for r in report_result.all()]
        
        if not report_ids:
            return {
                "by_severity": {},
                "by_category": {},
                "total": 0,
            }
        
        # Get findings
        findings_result = await db.execute(
            select(Finding).where(Finding.report_id.in_(report_ids))
        )
        findings = findings_result.scalars().all()
        
        # Get rules
        rule_ids = {f.rule_id for f in findings}
        rules = {}
        if rule_ids:
            rule_result = await db.execute(
                select(Rule).where(Rule.id.in_(rule_ids))
            )
            rules = {r.id: r for r in rule_result.scalars().all()}
        
        # Aggregate by severity
        by_severity = {}
        by_category = {}
        
        for finding in findings:
            # By severity
            severity = finding.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # By category
            rule = rules.get(finding.rule_id)
            if rule:
                category = rule.category
                by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "by_severity": by_severity,
            "by_category": by_category,
            "total": len(findings),
        }
    except Exception as e:
        logger.error(f"Error getting findings summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/facilities/comparison")
async def compare_facilities(
    tenant_id: int = Query(..., description="Tenant ID"),
    facility_ids: str = Query(..., description="Comma-separated facility IDs"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db_session),
):
    """Compare multiple facilities."""
    try:
        facility_id_list = [int(fid.strip()) for fid in facility_ids.split(",")]
        
        query = select(Report).where(
            and_(
                Report.tenant_id == tenant_id,
                Report.facility_id.in_(facility_id_list),
            )
        )
        
        if start_date:
            query = query.where(Report.clinic_date >= start_date)
        if end_date:
            query = query.where(Report.clinic_date <= end_date)
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Get facilities
        facility_result = await db.execute(
            select(Facility).where(Facility.id.in_(facility_id_list))
        )
        facilities = {f.id: f for f in facility_result.scalars().all()}
        
        # Get findings
        report_ids = {r.id for r in reports}
        findings = []
        if report_ids:
            findings_result = await db.execute(
                select(Finding).where(Finding.report_id.in_(report_ids))
            )
            findings = findings_result.scalars().all()
        
        # Aggregate by facility
        comparison = {}
        for facility_id in facility_id_list:
            facility = facilities.get(facility_id)
            facility_reports = [r for r in reports if r.facility_id == facility_id]
            facility_findings = [f for f in findings if f.report_id in {r.id for r in facility_reports}]
            
            comparison[facility_id] = {
                "facility": {
                    "id": facility.id if facility else facility_id,
                    "name": facility.name if facility else f"Facility {facility_id}",
                    "type": facility.type if facility else None,
                    "district": facility.district if facility else None,
                },
                "reports_count": len(facility_reports),
                "findings_count": len(facility_findings),
                "high_severity_findings": len([f for f in facility_findings if f.severity == "high"]),
            }
        
        return {
            "comparison": comparison,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
        }
    except Exception as e:
        logger.error(f"Error comparing facilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
