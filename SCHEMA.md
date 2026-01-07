# Canonical PPC Report JSON Schema

## Overview

This schema defines the canonical structure for Preconception/Maternal Health Clinic (PPC) reports. Every ingested document MUST be converted to this format, even if incomplete.

## Schema Principles

1. **Explicit Nulls**: Missing data represented as `null` with `missing_reason`
2. **Confidence Scores**: Extracted values include confidence where applicable
3. **Source Traceability**: Link back to original document positions
4. **Extensible**: Additional fields can be added without breaking existing structure
5. **Validation-Ready**: Structure supports automated validation rules

## Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["document_metadata", "facility", "clinic_details"],
  "properties": {

    "document_metadata": {
      "type": "object",
      "required": ["document_id", "ingestion_timestamp", "schema_version"],
      "properties": {
        "document_id": {
          "type": "string",
          "description": "Unique identifier for this document"
        },
        "ingestion_timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "When document was ingested (ISO 8601)"
        },
        "schema_version": {
          "type": "string",
          "description": "Version of this schema (semantic versioning)",
          "example": "1.0.0"
        },
        "source_file": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "file_type": {"type": "string", "enum": ["DOCX", "PDF", "IMAGE"]},
            "file_size_bytes": {"type": "integer"},
            "checksum": {"type": "string", "description": "SHA-256 hash"}
          }
        },
        "processing_metadata": {
          "type": "object",
          "properties": {
            "parser_version": {"type": "string"},
            "processing_duration_ms": {"type": "integer"},
            "extraction_quality_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Overall confidence in extraction (0-1)"
            }
          }
        }
      }
    },

    "facility": {
      "type": "object",
      "required": ["name", "type", "block", "district", "state"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Facility name",
          "example": "CHC Badsali"
        },
        "type": {
          "type": "string",
          "enum": ["CHC", "PHC", "Sub-Center", "District Hospital"],
          "description": "Facility type"
        },
        "block": {
          "type": "string",
          "description": "Block name",
          "example": "Haroli"
        },
        "district": {
          "type": "string",
          "description": "District name",
          "example": "Una"
        },
        "state": {
          "type": "string",
          "description": "State name",
          "example": "Himachal Pradesh"
        },
        "facility_code": {
          "type": "string",
          "description": "Government facility ID code"
        },
        "contact": {
          "type": "object",
          "properties": {
            "phone": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "in_charge_name": {"type": "string"}
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "clinic_details": {
      "type": "object",
      "required": ["date", "day_of_week"],
      "properties": {
        "date": {
          "type": "string",
          "format": "date",
          "description": "Clinic date (YYYY-MM-DD)",
          "example": "2025-12-04"
        },
        "day_of_week": {
          "type": "string",
          "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        },
        "time": {
          "type": "object",
          "properties": {
            "start": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"},
            "end": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}
          }
        },
        "clinic_type": {
          "type": "string",
          "enum": ["Regular", "Special", "Outreach", "Camp"],
          "default": "Regular"
        },
        "reported_by": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "designation": {"type": "string"},
            "phone": {"type": "string"}
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "clinic_setup": {
      "type": "object",
      "description": "Physical setup and infrastructure",
      "properties": {
        "dedicated_space": {
          "type": "object",
          "properties": {
            "available": {"type": "boolean"},
            "type": {
              "type": "string",
              "enum": ["single_room", "multiple_rooms", "shared_space", "none"]
            },
            "gap_description": {
              "type": "string",
              "description": "Free-text description of space issues"
            },
            "gap_description_normalized": {
              "type": "array",
              "items": {"$ref": "#/definitions/normalized_phrase"},
              "description": "Normalized intents extracted from gap description"
            }
          }
        },
        "privacy_maintained": {
          "type": "boolean",
          "description": "Is privacy ensured for consultations?"
        },
        "waiting_area": {
          "type": "object",
          "properties": {
            "available": {"type": "boolean"},
            "seating_capacity": {"type": "integer", "minimum": 0}
          }
        },
        "signage": {
          "type": "object",
          "properties": {
            "ppc_board_displayed": {"type": "boolean"},
            "directions_clear": {"type": "boolean"}
          }
        },
        "infrastructure_gaps": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "gap_type": {
                "type": "string",
                "enum": ["space", "equipment", "supplies", "staffing", "other"]
              },
              "description": {"type": "string"},
              "normalized_intents": {
                "type": "array",
                "items": {"$ref": "#/definitions/normalized_phrase"}
              },
              "severity": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"]
              }
            }
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "beneficiaries": {
      "type": "object",
      "required": ["expected_count", "actual_count"],
      "properties": {
        "expected_count": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of beneficiaries expected based on due list"
        },
        "actual_count": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of beneficiaries who actually attended"
        },
        "attendance_rate": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Calculated: actual_count / expected_count"
        },
        "attendance_barriers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "raw_reason": {
                "type": "string",
                "description": "Original text from document"
              },
              "normalized_intent": {
                "type": "string",
                "description": "Canonical intent code",
                "examples": [
                  "REASON_HUSBAND_ACCIDENT",
                  "REASON_BENEFICIARY_AT_MATERNAL_HOME",
                  "ASHA_COMMUNICATION_FAILURE",
                  "REASON_FAMILY_EMERGENCY",
                  "REASON_WORK_CONFLICT",
                  "REASON_ILLNESS",
                  "REASON_TRAVEL",
                  "REASON_UNAWARE"
                ]
              },
              "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
              },
              "category": {
                "type": "string",
                "enum": [
                  "PERSONAL_EMERGENCY",
                  "COMMUNICATION_FAILURE",
                  "LOGISTICS",
                  "CULTURAL_SOCIAL",
                  "HEALTH_RELATED",
                  "ECONOMIC",
                  "UNKNOWN"
                ]
              },
              "count": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of beneficiaries with this reason"
              }
            },
            "required": ["raw_reason", "normalized_intent", "confidence"]
          }
        },
        "individual_records": {
          "type": "array",
          "description": "Individual beneficiary records (if available)",
          "items": {
            "type": "object",
            "properties": {
              "beneficiary_id": {"type": "string"},
              "name": {"type": "string"},
              "age": {"type": "integer", "minimum": 10, "maximum": 60},
              "attended": {"type": "boolean"},
              "non_attendance_reason": {
                "type": "object",
                "properties": {
                  "raw_reason": {"type": "string"},
                  "normalized_intent": {"type": "string"},
                  "confidence": {"type": "number"}
                }
              }
            }
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "asha_performance": {
      "type": "object",
      "description": "ASHA worker mobilization effectiveness",
      "properties": {
        "asha_name": {"type": "string"},
        "asha_id": {"type": "string"},
        "mobilization_activities": {
          "type": "object",
          "properties": {
            "home_visits_conducted": {"type": "integer", "minimum": 0},
            "beneficiaries_informed": {"type": "integer", "minimum": 0},
            "advance_notice_days": {"type": "integer", "minimum": 0},
            "methods_used": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": ["home_visit", "phone_call", "sms", "community_meeting", "other"]
              }
            }
          }
        },
        "performance_issues": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "issue_raw": {"type": "string"},
              "issue_normalized": {
                "type": "string",
                "examples": [
                  "ASHA_COMMUNICATION_FAILURE",
                  "ASHA_INSUFFICIENT_HOME_VISITS",
                  "ASHA_LATE_NOTIFICATION",
                  "ASHA_INCORRECT_INFORMATION"
                ]
              },
              "confidence": {"type": "number"},
              "severity": {"type": "string", "enum": ["low", "medium", "high"]}
            }
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "clinical_services": {
      "type": "object",
      "description": "Services provided during clinic",
      "properties": {
        "staff_present": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "designation": {
                "type": "string",
                "enum": ["Medical Officer", "Staff Nurse", "ANM", "Pharmacist", "Lab Technician", "Other"]
              },
              "name": {"type": "string"},
              "present": {"type": "boolean"}
            }
          }
        },
        "services_provided": {
          "type": "object",
          "properties": {
            "physical_examination": {
              "type": "object",
              "properties": {
                "conducted": {"type": "boolean"},
                "beneficiaries_examined": {"type": "integer", "minimum": 0},
                "parameters_checked": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "enum": [
                      "height",
                      "weight",
                      "bmi",
                      "blood_pressure",
                      "pulse",
                      "temperature",
                      "pallor",
                      "thyroid_examination",
                      "breast_examination",
                      "abdominal_examination"
                    ]
                  }
                }
              }
            },
            "counselling": {
              "type": "object",
              "properties": {
                "nutrition": {"type": "boolean"},
                "exercise": {"type": "boolean"},
                "family_planning": {"type": "boolean"},
                "birth_spacing": {"type": "boolean"},
                "anemia_prevention": {"type": "boolean"},
                "hygiene": {"type": "boolean"},
                "danger_signs": {"type": "boolean"}
              }
            },
            "investigations": {
              "type": "object",
              "properties": {
                "lab_tests_conducted": {"type": "boolean"},
                "tests_list": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "enum": [
                      "hemoglobin",
                      "blood_sugar_fasting",
                      "blood_sugar_pp",
                      "thyroid_tsh",
                      "urine_routine",
                      "hiv",
                      "hbsag",
                      "vdrl",
                      "blood_group",
                      "other"
                    ]
                  }
                }
              }
            },
            "medications_distributed": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "medication": {
                    "type": "string",
                    "enum": ["IFA_tablets", "calcium", "folic_acid", "deworming", "other"]
                  },
                  "quantity": {"type": "string"},
                  "beneficiaries_received": {"type": "integer"}
                }
              }
            }
          }
        },
        "service_gaps": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "service": {"type": "string"},
              "gap_description": {"type": "string"},
              "normalized_intents": {
                "type": "array",
                "items": {"$ref": "#/definitions/normalized_phrase"}
              },
              "reason": {
                "type": "string",
                "enum": [
                  "staff_absent",
                  "equipment_unavailable",
                  "supplies_out_of_stock",
                  "time_constraint",
                  "beneficiary_refused",
                  "other"
                ]
              }
            }
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "laboratory": {
      "type": "object",
      "description": "Laboratory services and sample handling",
      "properties": {
        "samples_collected": {
          "type": "integer",
          "minimum": 0
        },
        "sample_types": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "test_name": {"type": "string"},
              "samples_count": {"type": "integer"},
              "collection_time": {"type": "string"}
            }
          }
        },
        "sample_storage": {
          "type": "object",
          "properties": {
            "storage_method": {
              "type": "string",
              "enum": ["refrigerated", "room_temperature", "ice_box", "not_specified"]
            },
            "storage_duration_hours": {
              "type": "number",
              "minimum": 0
            },
            "cold_chain_maintained": {
              "type": "boolean"
            },
            "violations": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "violation_raw": {"type": "string"},
                  "violation_normalized": {
                    "type": "string",
                    "examples": [
                      "LAB_SAMPLE_STORAGE_VIOLATION",
                      "LAB_COLD_CHAIN_BREAK",
                      "LAB_EXCESSIVE_DELAY"
                    ]
                  },
                  "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                }
              }
            }
          }
        },
        "sample_transport": {
          "type": "object",
          "properties": {
            "transported_to": {"type": "string"},
            "transport_method": {"type": "string"},
            "transport_time": {"type": "string"}
          }
        },
        "results_received": {
          "type": "boolean"
        },
        "results_shared_with_beneficiaries": {
          "type": "boolean"
        },
        "result_turnaround_time_days": {
          "type": "number",
          "minimum": 0
        },
        "lab_issues": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "issue_raw": {"type": "string"},
              "issue_normalized": {
                "type": "string",
                "examples": [
                  "LAB_CAPACITY_OVERLOAD",
                  "LAB_EQUIPMENT_UNAVAILABLE",
                  "LAB_STAFF_ABSENT",
                  "LAB_REAGENT_SHORTAGE"
                ]
              },
              "impact": {"type": "string"}
            }
          }
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "compliance": {
      "type": "object",
      "description": "Protocol and guideline compliance",
      "properties": {
        "due_list_prepared": {
          "type": "boolean"
        },
        "registers_updated": {
          "type": "boolean"
        },
        "reporting_timely": {
          "type": "boolean"
        },
        "iec_materials_displayed": {
          "type": "boolean",
          "description": "Information, Education, Communication materials"
        },
        "protocol_deviations": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "protocol": {"type": "string"},
              "deviation_description": {"type": "string"},
              "reason": {"type": "string"}
            }
          }
        }
      }
    },

    "observations": {
      "type": "object",
      "description": "Free-text observations and notes",
      "properties": {
        "field_worker_notes": {
          "type": "string",
          "description": "Original notes from field worker"
        },
        "supervisor_comments": {
          "type": "string"
        },
        "challenges_faced": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "challenge_raw": {"type": "string"},
              "challenge_normalized": {
                "type": "array",
                "items": {"$ref": "#/definitions/normalized_phrase"}
              }
            }
          }
        },
        "good_practices": {
          "type": "array",
          "items": {"type": "string"}
        },
        "extraction_metadata": {
          "$ref": "#/definitions/extraction_metadata"
        }
      }
    },

    "quality_indicators": {
      "type": "object",
      "description": "Calculated quality metrics (auto-computed)",
      "properties": {
        "data_completeness_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Proportion of required fields populated"
        },
        "compliance_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "process_adherence_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "risk_level": {
          "type": "string",
          "enum": ["low", "medium", "high", "critical"]
        },
        "flags": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "rule_id": {"type": "string"},
              "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
              "category": {"type": "string"},
              "message": {"type": "string"},
              "evidence": {"type": "object"}
            }
          }
        }
      }
    }
  },

  "definitions": {
    "extraction_metadata": {
      "type": "object",
      "description": "Metadata about how this section was extracted",
      "properties": {
        "extraction_confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Confidence in extraction accuracy (0-1)"
        },
        "source_text_position": {
          "type": "object",
          "properties": {
            "page": {"type": "integer"},
            "section": {"type": "string"},
            "line_start": {"type": "integer"},
            "line_end": {"type": "integer"}
          }
        },
        "missing_fields": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "field_name": {"type": "string"},
              "missing_reason": {
                "type": "string",
                "enum": ["not_found", "unreadable", "ambiguous", "not_applicable"]
              }
            }
          }
        },
        "extraction_notes": {
          "type": "string",
          "description": "Human-readable notes about extraction issues"
        }
      }
    },

    "normalized_phrase": {
      "type": "object",
      "description": "A phrase that has been normalized to a canonical intent",
      "required": ["raw_phrase", "canonical_intent", "confidence"],
      "properties": {
        "raw_phrase": {
          "type": "string",
          "description": "Original phrase from document"
        },
        "canonical_intent": {
          "type": "string",
          "description": "Normalized intent code"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Confidence in normalization (0-1)"
        },
        "category": {
          "type": "string",
          "description": "High-level category of this intent"
        },
        "severity": {
          "type": "string",
          "enum": ["low", "medium", "high", "critical"]
        },
        "match_method": {
          "type": "string",
          "enum": ["exact", "fuzzy", "semantic", "manual"],
          "description": "How this phrase was matched"
        }
      }
    }
  }
}
```

## Example: Complete PPC Report

```json
{
  "document_metadata": {
    "document_id": "doc_2025_hp_una_001",
    "ingestion_timestamp": "2025-01-07T10:30:00Z",
    "schema_version": "1.0.0",
    "source_file": {
      "filename": "CHC_Badsali_PPC_04Dec2025.docx",
      "file_type": "DOCX",
      "file_size_bytes": 45632,
      "checksum": "a1b2c3d4..."
    },
    "processing_metadata": {
      "parser_version": "1.0.0",
      "processing_duration_ms": 3421,
      "extraction_quality_score": 0.87
    }
  },

  "facility": {
    "name": "CHC Badsali",
    "type": "CHC",
    "block": "Haroli",
    "district": "Una",
    "state": "Himachal Pradesh",
    "facility_code": "HP_UNA_CHC_001",
    "contact": {
      "phone": "+91-1234567890",
      "in_charge_name": "Dr. Sharma"
    },
    "extraction_metadata": {
      "extraction_confidence": 0.95,
      "source_text_position": {
        "page": 1,
        "section": "Facility Details"
      }
    }
  },

  "clinic_details": {
    "date": "2025-12-04",
    "day_of_week": "Wednesday",
    "time": {
      "start": "10:00",
      "end": "13:30"
    },
    "clinic_type": "Regular",
    "reported_by": {
      "name": "Sister Meena",
      "designation": "Staff Nurse",
      "phone": "+91-9876543210"
    }
  },

  "clinic_setup": {
    "dedicated_space": {
      "available": true,
      "type": "multiple_rooms",
      "gap_description": "Shared OPD with general patients during peak hours",
      "gap_description_normalized": [
        {
          "raw_phrase": "shared OPD with general patients",
          "canonical_intent": "SPACE_SHARED_WITH_GENERAL_OPD",
          "confidence": 0.92,
          "category": "INFRASTRUCTURE_GAP",
          "severity": "medium"
        }
      ]
    },
    "privacy_maintained": true,
    "waiting_area": {
      "available": true,
      "seating_capacity": 12
    },
    "signage": {
      "ppc_board_displayed": true,
      "directions_clear": true
    },
    "infrastructure_gaps": []
  },

  "beneficiaries": {
    "expected_count": 8,
    "actual_count": 1,
    "attendance_rate": 0.125,
    "attendance_barriers": [
      {
        "raw_reason": "asha nai btaya tha",
        "normalized_intent": "ASHA_COMMUNICATION_FAILURE",
        "confidence": 0.89,
        "category": "COMMUNICATION_FAILURE",
        "count": 3
      },
      {
        "raw_reason": "mayke gyi thi",
        "normalized_intent": "REASON_BENEFICIARY_AT_MATERNAL_HOME",
        "confidence": 0.93,
        "category": "CULTURAL_SOCIAL",
        "count": 2
      },
      {
        "raw_reason": "pti ka exident ho gya",
        "normalized_intent": "REASON_HUSBAND_ACCIDENT",
        "confidence": 0.87,
        "category": "PERSONAL_EMERGENCY",
        "count": 1
      },
      {
        "raw_reason": "family emergency",
        "normalized_intent": "REASON_FAMILY_EMERGENCY",
        "confidence": 0.95,
        "category": "PERSONAL_EMERGENCY",
        "count": 1
      }
    ],
    "individual_records": [
      {
        "beneficiary_id": "BEN_001",
        "name": "Priya Devi",
        "age": 24,
        "attended": true
      }
    ],
    "extraction_metadata": {
      "extraction_confidence": 0.85,
      "source_text_position": {
        "page": 2,
        "section": "Beneficiary Attendance"
      }
    }
  },

  "asha_performance": {
    "asha_name": "Sunita",
    "mobilization_activities": {
      "home_visits_conducted": 5,
      "beneficiaries_informed": 5,
      "advance_notice_days": 2,
      "methods_used": ["home_visit", "phone_call"]
    },
    "performance_issues": [
      {
        "issue_raw": "3 families ko inform nahi kiya",
        "issue_normalized": "ASHA_INSUFFICIENT_COVERAGE",
        "confidence": 0.88,
        "severity": "high"
      }
    ]
  },

  "clinical_services": {
    "staff_present": [
      {
        "designation": "Medical Officer",
        "name": "Dr. Kumar",
        "present": true
      },
      {
        "designation": "Staff Nurse",
        "name": "Sister Meena",
        "present": true
      },
      {
        "designation": "Lab Technician",
        "name": "Rajesh",
        "present": true
      }
    ],
    "services_provided": {
      "physical_examination": {
        "conducted": true,
        "beneficiaries_examined": 1,
        "parameters_checked": [
          "height",
          "weight",
          "bmi",
          "blood_pressure",
          "pulse"
        ]
      },
      "counselling": {
        "nutrition": true,
        "exercise": false,
        "family_planning": true,
        "birth_spacing": true,
        "anemia_prevention": true,
        "hygiene": true,
        "danger_signs": true
      },
      "investigations": {
        "lab_tests_conducted": true,
        "tests_list": [
          "hemoglobin",
          "blood_sugar_fasting",
          "thyroid_tsh",
          "urine_routine"
        ]
      },
      "medications_distributed": [
        {
          "medication": "IFA_tablets",
          "quantity": "30 tablets",
          "beneficiaries_received": 1
        },
        {
          "medication": "calcium",
          "quantity": "30 tablets",
          "beneficiaries_received": 1
        }
      ]
    },
    "service_gaps": [
      {
        "service": "Exercise counselling",
        "gap_description": "Not provided to beneficiary with BMI 26.3",
        "normalized_intents": [
          {
            "raw_phrase": "exercise counselling not given",
            "canonical_intent": "COUNSELLING_EXERCISE_MISSING",
            "confidence": 0.90,
            "category": "PROTOCOL_DEVIATION",
            "severity": "medium"
          }
        ],
        "reason": "time_constraint"
      }
    ]
  },

  "laboratory": {
    "samples_collected": 4,
    "sample_types": [
      {
        "test_name": "Hemoglobin",
        "samples_count": 1,
        "collection_time": "10:30"
      },
      {
        "test_name": "Blood Sugar Fasting",
        "samples_count": 1,
        "collection_time": "10:35"
      },
      {
        "test_name": "Thyroid TSH",
        "samples_count": 1,
        "collection_time": "10:40"
      },
      {
        "test_name": "Urine Routine",
        "samples_count": 1,
        "collection_time": "10:45"
      }
    ],
    "sample_storage": {
      "storage_method": "refrigerated",
      "storage_duration_hours": 3,
      "cold_chain_maintained": true,
      "violations": []
    },
    "sample_transport": {
      "transported_to": "District Hospital Lab",
      "transport_method": "Cold box via ambulance",
      "transport_time": "14:00"
    },
    "results_received": false,
    "results_shared_with_beneficiaries": false,
    "result_turnaround_time_days": null
  },

  "compliance": {
    "due_list_prepared": true,
    "registers_updated": true,
    "reporting_timely": true,
    "iec_materials_displayed": true,
    "protocol_deviations": [
      {
        "protocol": "Exercise counselling for overweight beneficiaries",
        "deviation_description": "Not provided to beneficiary with BMI 26.3",
        "reason": "Time constraint due to low turnout"
      }
    ]
  },

  "observations": {
    "field_worker_notes": "Very low turnout due to ASHA mobilization issues. Need to improve communication and advance planning. One beneficiary received good quality services.",
    "challenges_faced": [
      {
        "challenge_raw": "asha ne time par inform nahi kiya",
        "challenge_normalized": [
          {
            "raw_phrase": "asha ne time par inform nahi kiya",
            "canonical_intent": "ASHA_LATE_NOTIFICATION",
            "confidence": 0.91,
            "category": "SYSTEM_FAILURE",
            "severity": "high"
          }
        ]
      }
    ],
    "good_practices": [
      "Thorough examination of attending beneficiary",
      "Complete counselling provided",
      "Proper cold chain maintenance"
    ]
  },

  "quality_indicators": {
    "data_completeness_score": 0.93,
    "compliance_score": 72,
    "process_adherence_score": 68,
    "risk_level": "medium",
    "flags": [
      {
        "rule_id": "R_PPC_005",
        "severity": "high",
        "category": "MOBILIZATION",
        "message": "Only 1 beneficiary attended vs. 8 expected (12.5% attendance rate)",
        "evidence": {
          "expected_count": 8,
          "actual_count": 1,
          "attendance_rate": 0.125
        }
      },
      {
        "rule_id": "R_PPC_001",
        "severity": "medium",
        "category": "PROTOCOL_VIOLATION",
        "message": "Beneficiary has BMI >= 25 but no exercise counselling recorded",
        "evidence": {
          "bmi": 26.3,
          "exercise_counselling_provided": false
        }
      },
      {
        "rule_id": "R_PPC_010",
        "severity": "high",
        "category": "SYSTEM_FAILURE",
        "message": "ASHA communication failure detected for 3 beneficiaries",
        "evidence": {
          "barrier": "ASHA_COMMUNICATION_FAILURE",
          "count": 3,
          "percentage": 37.5
        }
      }
    ]
  }
}
```

## Schema Evolution Strategy

### Versioning
- Semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (field removal, type change)
- MINOR: New fields (backward compatible)
- PATCH: Documentation, clarifications

### Backward Compatibility
- Old documents can always be read
- New parsers support old schemas
- Migration scripts for major version changes

### Extension Points
- Each section can have `additional_data` object for program-specific fields
- Custom fields prefixed with `custom_`
- Maintain core schema stability

## Validation Rules

### Required Field Validation
- `document_metadata`, `facility`, `clinic_details` are mandatory
- Other sections can be null but must be explicitly marked

### Data Type Validation
- Strict type checking (string, integer, boolean, etc.)
- Date format: ISO 8601
- Phone: E.164 format recommended

### Business Logic Validation
- `attendance_rate` = `actual_count` / `expected_count`
- `extraction_confidence` between 0 and 1
- Scores between 0 and 100

### Cross-Field Validation
- If `lab_tests_conducted` = true, `sample_storage` must be present
- If `actual_count` < `expected_count`, `attendance_barriers` should be present

## Implementation Notes

1. **Parser Output**: All parsers must produce JSON conforming to this schema
2. **Database Storage**: Store as JSONB in PostgreSQL for querying
3. **API Responses**: Serve this format via REST API
4. **Frontend Consumption**: TypeScript interfaces generated from schema
5. **Validation**: JSON Schema validation before database insert

## Schema Maintenance

- Schema definition stored in version control
- Changes reviewed like code
- Migration scripts for schema updates
- Documentation updated with each change
- Test data samples for each version
