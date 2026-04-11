from collections import Counter
from app.core.config import VALID_SEX_VALUES, VALID_VACCINATION_STATUES
from app.models.anomaly import Anomaly
from app.models.breed_rule import BreedRule
from app.models.dog_record import DogRecord

class ValidatorService:
    def validate_records(
            self,
            dog_records: list[DogRecord],
            breed_rules: dict[str, BreedRule]
    ) -> list[Anomaly]:
        anomalies: list[Anomaly] = []
        duplicates = self._detect_duplicates(dog_records)
        for record in dog_records:
            anomalies.extend(self._validate_breed_exists(record, breed_rules))
            anomalies.extend(self._validate_sex(record))
            anomalies.extend(self._validate_vaccination_status(record))
            anomalies.extend(self._validate_image_path(record))

            breed_rule = breed_rules.get(record.breed.lower())
            if breed_rule:
                anomalies.extend(self._validate_weight(record, breed_rule))
                anomalies.extend(self._validate_age(record, breed_rule))
                anomalies.extend(self._validate_category(record, breed_rule))

            if record.dog_id in duplicates:
                anomalies.append(
                    Anomaly(
                        dog_id=record.dog_id,
                        dog_name=record.dog_name,
                        anomaly_type="registro_duplicado",
                        severity="alta",
                        message="Registro duplicado según nombre, raza, propietario, fecha e imagen.",
                    )
                )
        return anomalies

    @staticmethod
    def _validate_breed_exists(
            record: DogRecord,
            breed_rules: dict[str, BreedRule],
    ) -> list[Anomaly]:
        if record.breed.lower() not in breed_rules:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="raza_no_válida",
                    severity="alta",
                    message=f"La raza '{record.breed}' no existe en el catálogo maestro.",
                )
            ]
        return []

    @staticmethod
    def _validate_age(record: DogRecord, breed_rule: BreedRule) -> list[Anomaly]:
        if not (breed_rule.min_age_months <= record.age_months <= breed_rule.max_age_months):
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="edad_fuera_rango",
                    severity="media",
                    message=(
                        f"La edad {record.age_months} meses está fuera del rango permitido "
                        f"para la raza {breed_rule.breed} "
                        f"({breed_rule.min_age_months} - {breed_rule.max_age_months} meses)."
                    ),
                )
            ]
        return []

    @staticmethod
    def _validate_category(record: DogRecord, breed_rule: BreedRule) -> list[Anomaly]:
        if record.competition_category not in breed_rule.allowed_categories:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="categoría_no_válida",
                    severity="alta",
                    message=(
                        f"La categoría '{record.competition_category}' no es válida para la raza "
                        f"{breed_rule.breed}. Categorías permitidas: {', '.join(breed_rule.allowed_categories)}."
                    ),
                )
            ]
        return []

    @staticmethod
    def _validate_vaccination_status(record: DogRecord) -> list[Anomaly]:
        if record.vaccination_status not in VALID_VACCINATION_STATUES:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="estado_vacunación_no_válido",
                    severity="medium",
                    message=(
                        f"El estado de vacunación '{record.vaccination_status}' no es válido. "
                        f"Valores permitidos: {', '.join(sorted(VALID_VACCINATION_STATUES))}."
                    ),
                )
            ]
        return []

    @staticmethod
    def _validate_sex(record: DogRecord) -> list[Anomaly]:
        if record.sex not in VALID_SEX_VALUES:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="sexo_no_válido",
                    severity="bajo",
                    message=f"El valor de sexo '{record.sex}' no es válido.",
                )
            ]
        return []

    @staticmethod
    def _validate_image_path(record: DogRecord) -> list[Anomaly]:
        if not record.image_path:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="sin_imagen",
                    severity="media",
                    message="El registro no tiene ruta de imagen asociada.",
                )
            ]
        return []

    @staticmethod
    def _detect_duplicates(dog_records: list[DogRecord]) -> set[int]:
        keys = [
            (
                record.dog_name.strip().lower(),
                record.breed.strip().lower(),
                record.owner_name.strip().lower(),
                record.registration_date.strip(),
                record.image_path.strip().lower(),
            )
            for record in dog_records
        ]

        counts = Counter(keys)
        duplicate_keys = {key for key, count in counts.items() if count > 1}

        duplicate_ids: set[int] = set()
        for record in dog_records:
            key = (
                record.dog_name.strip().lower(),
                record.breed.strip().lower(),
                record.owner_name.strip().lower(),
                record.registration_date.strip(),
                record.image_path.strip().lower(),
            )
            if key in duplicate_keys:
                duplicate_ids.add(record.dog_id)

        return duplicate_ids

    @staticmethod
    def _validate_weight(record: DogRecord, breed_rule: BreedRule) -> list[Anomaly]:
        if not (breed_rule.min_weight_kg <= record.weight_kg <= breed_rule.max_weight_kg):
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="peso_fuera_de_rango",
                    severity="high",
                    message=(
                        f"El peso {record.weight_kg} kg está fuera del rango permitido "
                        f"para la raza {breed_rule.breed} "
                        f"({breed_rule.min_weight_kg} - {breed_rule.max_weight_kg} kg)."
                    ),
                )
            ]
        return []