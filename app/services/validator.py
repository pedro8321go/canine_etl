from collections import Counter
from datetime import date, datetime
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
            anomalies.extend(self._validate_registration_date_vs_age(record))

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
                        issue_level="error",
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
                    issue_level="error",
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
                    issue_level="warning",
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
                    issue_level="error",
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
                    issue_level="warning",
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
                    issue_level="error",
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
                    issue_level="warning",
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
                    issue_level="error",
                    message=(
                        f"El peso {record.weight_kg} kg está fuera del rango permitido "
                        f"para la raza {breed_rule.breed} "
                        f"({breed_rule.min_weight_kg} - {breed_rule.max_weight_kg} kg)."
                    ),
                )
            ]
        return []

    @staticmethod
    def _validate_registration_date_vs_age(record: DogRecord) -> list[Anomaly]:
        try:
            registration_date = datetime.strptime(record.registration_date, "%Y-%m-%d").date()
        except ValueError:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="fecha_inscripcion_formato_invalido",
                    issue_level="error",
                    message=(
                        f"La fecha de inscripción '{record.registration_date}' no tiene formato YYYY-MM-DD."
                    ),
                )
            ]

        today = date.today()
        if registration_date > today:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="fecha_inscripcion_futura",
                    issue_level="error",
                    message=(
                        f"La fecha de inscripción '{record.registration_date}' no puede ser posterior a hoy."
                    ),
                )
            ]

        earliest_possible_registration = ValidatorService._subtract_months(today, record.age_months)
        if registration_date < earliest_possible_registration:
            return [
                Anomaly(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    anomaly_type="fecha_inscripcion_incompatible_edad",
                    issue_level="error",
                    message=(
                        f"La fecha de inscripción '{record.registration_date}' es anterior a la fecha mínima "
                        f"compatible con la edad del perro ({record.age_months} meses)."
                    ),
                )
            ]

        return []

    @staticmethod
    def _subtract_months(reference_date: date, months: int) -> date:
        year = reference_date.year
        month = reference_date.month - months
        while month <= 0:
            month += 12
            year -= 1

        day = min(reference_date.day, ValidatorService._days_in_month(year, month))
        return date(year, month, day)

    @staticmethod
    def _days_in_month(year: int, month: int) -> int:
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        return (next_month - date(year, month, 1)).days
