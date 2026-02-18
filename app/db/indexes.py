"""Database indexes for optimal query performance."""

# This file contains SQL for creating indexes that optimize common queries
# Run these after initial migrations

INDEXES_SQL = """
-- Documents table indexes
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);

-- Reports table indexes (critical for performance)
CREATE INDEX IF NOT EXISTS idx_reports_facility_date ON reports(facility_id, clinic_date DESC);
CREATE INDEX IF NOT EXISTS idx_reports_document_id ON reports(document_id);
CREATE INDEX IF NOT EXISTS idx_reports_clinic_date ON reports(clinic_date DESC);
CREATE INDEX IF NOT EXISTS idx_reports_schema_version ON reports(schema_version);

-- JSONB indexes for efficient querying of report data
CREATE INDEX IF NOT EXISTS idx_reports_data_facility_name ON reports USING gin((data->'facility'->>'name'));
CREATE INDEX IF NOT EXISTS idx_reports_data_district ON reports USING gin((data->'facility'->>'district'));
CREATE INDEX IF NOT EXISTS idx_reports_data_state ON reports USING gin((data->'facility'->>'state'));
CREATE INDEX IF NOT EXISTS idx_reports_data_attendance_rate ON reports USING btree(((data->'beneficiaries'->>'attendance_rate')::float));

-- Quality indicators indexes
CREATE INDEX IF NOT EXISTS idx_reports_compliance_score ON reports USING btree(((quality_indicators->>'compliance_score')::int));
CREATE INDEX IF NOT EXISTS idx_reports_risk_level ON reports USING btree((quality_indicators->>'risk_level'));

-- Findings table indexes
CREATE INDEX IF NOT EXISTS idx_findings_report_severity ON findings(report_id, severity);
CREATE INDEX IF NOT EXISTS idx_findings_rule_id ON findings(rule_id);
CREATE INDEX IF NOT EXISTS idx_findings_created_at ON findings(created_at DESC);

-- Facilities table indexes
CREATE INDEX IF NOT EXISTS idx_facilities_code ON facilities(facility_code);
CREATE INDEX IF NOT EXISTS idx_facilities_district_state ON facilities(district, state);
CREATE INDEX IF NOT EXISTS idx_facilities_type ON facilities(type);

-- Rules table indexes
CREATE INDEX IF NOT EXISTS idx_rules_active ON rules(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category);
CREATE INDEX IF NOT EXISTS idx_rules_severity ON rules(severity);

-- Phrase dictionary indexes
CREATE INDEX IF NOT EXISTS idx_phrase_dict_active ON phrase_dictionary(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_phrase_dict_intent ON phrase_dictionary(canonical_intent);
CREATE INDEX IF NOT EXISTS idx_phrase_dict_category ON phrase_dictionary(category);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_reports_facility_date_status ON reports(facility_id, clinic_date DESC, (quality_indicators->>'risk_level'));
CREATE INDEX IF NOT EXISTS idx_findings_report_severity_created ON findings(report_id, severity, created_at DESC);

-- Partial indexes for better performance on filtered queries
CREATE INDEX IF NOT EXISTS idx_reports_high_risk ON reports(facility_id, clinic_date DESC) 
    WHERE (quality_indicators->>'risk_level') IN ('high', 'critical');
    
CREATE INDEX IF NOT EXISTS idx_findings_critical ON findings(report_id, created_at DESC) 
    WHERE severity = 'critical';
"""

# Performance optimization settings
PERFORMANCE_SETTINGS_SQL = """
-- Enable query performance monitoring
ALTER DATABASE ghda_saas SET log_min_duration_statement = 1000;  -- Log slow queries >1s
ALTER DATABASE ghda_saas SET shared_preload_libraries = 'pg_stat_statements';

-- Optimize for JSONB operations
ALTER DATABASE ghda_saas SET work_mem = '16MB';
ALTER DATABASE ghda_saas SET maintenance_work_mem = '256MB';
"""
