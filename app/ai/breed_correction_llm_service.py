import json

from app.ai.llm_client import LLMClient
from app.ai.prompts import build_breed_correction_prompt
from app.ai.schemas import LLM_BREED_CORRECTION_JSON_SCHEMA
from app.models.anomaly import Anomaly
from app.models.breed_rule import BreedRule
from app.models.dog_record import DogRecord


class BreedCorrectionLLMService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def correct_invalid_breeds(
        self,
        dog_records: list[DogRecord],
        breed_rules: dict[str, BreedRule],
    ) -> list[Anomaly]:
        invalid_breeds = sorted(
            {record.breed for record in dog_records if record.breed.lower() not in breed_rules}
        )
        if not invalid_breeds:
            return []

        allowed_breeds = sorted({rule.breed for rule in breed_rules.values()})
        prompt = build_breed_correction_prompt(
            invalid_breeds_json=json.dumps(invalid_breeds, ensure_ascii=False, separators=(",", ":")),
            allowed_breeds_json=json.dumps(allowed_breeds, ensure_ascii=False, separators=(",", ":")),
        )
        response = self.llm_client.generate_structured_json(
            prompt=prompt,
            json_schema=LLM_BREED_CORRECTION_JSON_SCHEMA,
            max_output_tokens=350,
        )
        corrections = response.get("corrections", [])
        if not isinstance(corrections, list):
            raise ValueError("Respuesta invalida de LLM en correccion de razas: 'corrections' no es lista.")

        allowed_by_lower = {breed.lower(): breed for breed in allowed_breeds}
        replacement_by_source_lower: dict[str, str] = {}
        for item in corrections:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source_breed", "")).strip()
            suggested = str(item.get("suggested_breed", "")).strip()
            should_replace = bool(item.get("should_replace", False))
            if not source or not suggested or not should_replace:
                continue

            canonical = allowed_by_lower.get(suggested.lower())
            if canonical:
                replacement_by_source_lower[source.lower()] = canonical

        correction_anomalies: list[Anomaly] = []
        for record in dog_records:
            source_lower = record.breed.lower()
            replacement = replacement_by_source_lower.get(source_lower)
            if not replacement or replacement.lower() == source_lower:
                continue

            original_breed = record.breed
            record.breed = replacement
            correction_anomalies.append(
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="raza_corregida_llm",
                    issue_level="warning",
                    message=(
                        f"Raza corregida por LLM de '{original_breed}' a '{replacement}' "
                        "usando catalogo maestro."
                    ),
                )
            )

        return correction_anomalies
