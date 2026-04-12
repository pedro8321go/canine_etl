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