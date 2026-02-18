"""GHDA-SaaS Database Models."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, ForeignKey, Text, Integer, Boolean, DateTime, Date, func
from typing import List, Dict, Any, Optional
from .base import Base, TimestampMixin

# Tenant model (multi-tenancy support)
class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    name: Mapped[str] = mapped_column(String, unique=True)
    domain: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    plan: Mapped[str] = mapped_column(String, default="starter")
    status: Mapped[str] = mapped_column(String, default="active")
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

# Document model
class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    
    filename: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)  # DOCX, PDF, IMAGE
    file_size: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(String, unique=True)
    storage_path: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

# Facility model
class Facility(Base, TimestampMixin):
    __tablename__ = "facilities"
    
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)  # CHC, PHC, Sub-Center, District Hospital
    block: Mapped[str] = mapped_column(String)
    district: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    facility_code: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    contact: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})

# Report model (parsed data stored as JSONB)
class Report(Base, TimestampMixin):
    __tablename__ = "reports"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    clinic_date: Mapped[Date] = mapped_column(Date)
    schema_version: Mapped[str] = mapped_column(String, default="1.0.0")
    data: Mapped[Dict[str, Any]] = mapped_column(JSON)  # Full canonical JSON
    quality_indicators: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))

# User model
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)  # admin, analyst, viewer
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))

# Rule model
class Rule(Base, TimestampMixin):
    __tablename__ = "rules"
    
    rule_id: Mapped[str] = mapped_column(String, unique=True)
    version: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    condition: Mapped[Dict[str, Any]] = mapped_column(JSON)
    action: Mapped[Dict[str, Any]] = mapped_column(JSON)
    evidence_fields: Mapped[List[str]] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))

# Finding model (rule evaluation results)
class Finding(Base, TimestampMixin):
    __tablename__ = "findings"
    
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id"))
    severity: Mapped[str] = mapped_column(String)
    flag: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON)

# Audit log model
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String)
    resource_type: Mapped[str] = mapped_column(String)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    changes: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
