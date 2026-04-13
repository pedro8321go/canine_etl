import json
import re
import unicodedata
from typing import Any

from app.ai.llm_client import LLMClient
from app.ai.prompts import build_semantic_validation_prompt
from app.ai.schemas import LLM_SEMANTIC_VALIDATION_JSON_SCHEMA
from app.models.anomaly import Anomaly
from app.models.breed_rule import BreedRule
from app.models.dog_record import DogRecord


class SemanticValidationLLMService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def validate_records(
        self,
        dog_records: list[DogRecord],
        breed_rules: dict[str, BreedRule],
    ) -> list[Anomaly]:
        records_with_notes = [record for record in dog_records if record.registration_notes.strip()]
        if not records_with_notes:
            return []

        allowed_breeds = sorted({rule.breed for rule in breed_rules.values()})

        dog_name_by_id = {record.dog_id: record.dog_name for record in dog_records}
        anomalies: list[Anomaly] = []
        batch_size = 10
        for batch_start in range(0, len(records_with_notes), batch_size):
            batch_records = records_with_notes[batch_start : batch_start + batch_size]

            payload_records: list[dict[str, Any]] = []
            for record in batch_records:
                payload_records.append(
                    {
                        "dog_id": record.dog_id,
                        "breed": record.breed,
                        "weight_kg": record.weight_kg,
                        "competition_category": record.competition_category,
                        "registration_notes": record.registration_notes,
                    }
                )

            prompt = build_semantic_validation_prompt(
                records_json=json.dumps(payload_records, ensure_ascii=False, separators=(",", ":")),
                allowed_breeds_json=json.dumps(allowed_breeds, ensure_ascii=False, separators=(",", ":")),
            )
            response = self.llm_client.generate_structured_json(
                prompt=prompt,
                json_schema=LLM_SEMANTIC_VALIDATION_JSON_SCHEMA,
                max_output_tokens=700,
            )

            record_by_id = {record.dog_id: record for record in batch_records}
            for item in response.get("items", []):
                if not bool(item.get("has_issue", False)):
                    continue

                dog_id_raw = item.get("dog_id")
                if not isinstance(dog_id_raw, int):
                    continue

                dog_name = dog_name_by_id.get(dog_id_raw)
                record = record_by_id.get(dog_id_raw)
                if not dog_name or not record:
                    continue

                issue_level = str(item.get("issue_level", "warning")).strip().lower()
                if issue_level not in {"warning", "error"}:
                    issue_level = "warning"

                issue_type = str(item.get("issue_type", "")).strip() or "inconsistencia_semantica"
                message = str(item.get("message", "")).strip()
                if not message:
                    message = "Posible inconsistencia semantica entre datos estructurados y nota."

                if not self._has_verifiable_semantic_mismatch(record, breed_rules):
                    continue

                anomalies.append(
                    Anomaly(
                        dog_id=dog_id_raw,
                        dog_name=dog_name,
                        anomaly_type=f"llm_{issue_type}",
                        issue_level=issue_level,
                        message=message,
                    )
                )

        return anomalies

    @staticmethod
    def _normalize(value: str) -> str:
        value = value.strip().lower()
        value = unicodedata.normalize("NFD", value)
        value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
        return value

    def _has_verifiable_semantic_mismatch(
        self,
        record: DogRecord,
        breed_rules: dict[str, BreedRule],
    ) -> bool:
        notes_norm = self._normalize(record.registration_notes)
        if not notes_norm:
            return False

        if self._has_weight_mismatch(notes_norm, record.weight_kg):
            return True

        if self._has_category_mismatch(notes_norm, record.competition_category, breed_rules):
            return True

        if self._has_size_mismatch(notes_norm, record.breed, breed_rules):
            return True

        if self._has_breed_mismatch(notes_norm, record.breed, breed_rules):
            return True

        return False

    @staticmethod
    def _has_weight_mismatch(notes_norm: str, structured_weight: float) -> bool:
        matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*kg", notes_norm)
        if not matches:
            return False

        for raw in matches:
            text_weight = float(raw.replace(",", "."))
            if abs(text_weight - structured_weight) >= 2.0:
                return True
        return False

    def _has_category_mismatch(
        self,
        notes_norm: str,
        structured_category: str,
        breed_rules: dict[str, BreedRule],
    ) -> bool:
        all_categories = {
            self._normalize(category)
            for rule in breed_rules.values()
            for category in rule.allowed_categories
        }
        mentioned_categories = {cat for cat in all_categories if cat and cat in notes_norm}
        if not mentioned_categories:
            return False

        structured_norm = self._normalize(structured_category)
        return structured_norm not in mentioned_categories

    def _has_size_mismatch(
        self,
        notes_norm: str,
        breed: str,
        breed_rules: dict[str, BreedRule],
    ) -> bool:
        rule = breed_rules.get(self._normalize(breed))
        if not rule:
            return False

        expected_size = self._normalize(rule.size_group)
        mentioned_sizes = set()
        for token in ["toy", "pequeno", "mediano", "grande", "gigante"]:
            if token in notes_norm:
                mentioned_sizes.add(token)

        if not mentioned_sizes:
            return False

        return expected_size not in mentioned_sizes

    def _has_breed_mismatch(
        self,
        notes_norm: str,
        structured_breed: str,
        breed_rules: dict[str, BreedRule],
    ) -> bool:
        mentioned_breeds = {
            self._normalize(rule.breed)
            for rule in breed_rules.values()
            if self._normalize(rule.breed) in notes_norm
        }
        if not mentioned_breeds:
            return False

        structured_breed_norm = self._normalize(structured_breed)
        return structured_breed_norm not in mentioned_breeds
