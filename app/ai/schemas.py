LLM_NARRATIVE_JSON_SCHEMA = {
    "name": "etl_narrative_summary",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "executive_summary": {
                "type": "string"
            },
            "main_issues": {
                "type": "array",
                "items": {"type": "string"}
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"}
            },
            "risk_assessment": {
                "type": "string"
            }
        },
        "required": [
            "executive_summary",
            "main_issues",
            "recommendations",
            "risk_assessment"
        ]
    }
}

LLM_BREED_CORRECTION_JSON_SCHEMA = {
    "name": "breed_corrections",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "corrections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "source_breed": {"type": "string"},
                        "suggested_breed": {"type": "string"},
                        "should_replace": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": [
                        "source_breed",
                        "suggested_breed",
                        "should_replace",
                        "reason",
                    ],
                },
            }
        },
        "required": ["corrections"],
    },
}
