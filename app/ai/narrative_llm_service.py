import json
from typing import Any

from app.ai.llm_client import LLMClient
from app.ai.prompts import build_etl_narrative_prompt
from app.ai.schemas import LLM_NARRATIVE_JSON_SCHEMA
from app.models.anomaly import Anomaly
from app.models.execution_summary import ExecutionSummary


class NarrativeLLMService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def generate_narrative_summary(
        self,
        summary: ExecutionSummary,
        anomalies: list[Anomaly],
        max_anomalies_preview: int = 5,
    ) -> dict[str, Any]:
        summary_json = json.dumps(
            summary.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

        preview_rows: list[list[Any]] = []
        for anomaly in anomalies[:max_anomalies_preview]:
            preview_rows.append(
                [
                    anomaly.dog_id,
                    anomaly.dog_name,
                    anomaly.anomaly_type,
                    anomaly.issue_level,
                    anomaly.message,
                ]
            )

        anomalies_preview = json.dumps(
            preview_rows,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        prompt = build_etl_narrative_prompt(
            summary_json=summary_json,
            anomalies_preview=anomalies_preview,
        )

        return self.llm_client.generate_structured_json(
            prompt=prompt,
            json_schema=LLM_NARRATIVE_JSON_SCHEMA,
        )
