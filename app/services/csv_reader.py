import pandas as pd
from app.models.breed_rule import BreedRule
from app.models.dog_record import DogRecord
from app.utils.text_normalizer import normalize_text

class CSVReaderService:
    BREED_RULES_REQUIRED_COLUMNS = {
        "breed",
        "min_weight_kg",
        "max_weight_kg",
        "min_age_months",
        "max_age_months",
        "size_group",
        "allowed_categories",
    }
    DOG_RECORDS_REQUIRED_COLUMNS = {
        "dog_id",
        "dog_name",
        "breed",
        "sex",
        "age_months",
        "weight_kg",
        "owner_name",
        "competition_category",
        "vaccination_status",
        "registration_date",
        "image_path",
    }

    @staticmethod
    def _assert_required_columns(df: pd.DataFrame, required_columns: set[str], file_path: str) -> None:
        missing_columns = sorted(required_columns - set(df.columns))
        if missing_columns:
            raise ValueError(
                f"CSV invalido en '{file_path}'. Faltan columnas requeridas: {', '.join(missing_columns)}"
            )

    @staticmethod
    def read_breed_rules(file_path: str) -> dict[str, BreedRule]:
        try:
            df = pd.read_csv(file_path)
        except Exception as exc:
            raise RuntimeError(f"No se pudo leer el archivo de reglas de raza: '{file_path}'") from exc
        CSVReaderService._assert_required_columns(df, CSVReaderService.BREED_RULES_REQUIRED_COLUMNS, file_path)

        bread_rules: dict[str, BreedRule] = {}
        for idx, row in df.iterrows():
            try:
                breed = normalize_text(row["breed"])
                allowed_categories = [
                    normalize_text(category)
                    for category in str(row["allowed_categories"]).split("|")
                ]
                bread_rules[breed.lower()] = BreedRule(
                    breed=breed,
                    min_weight_kg=float(row["min_weight_kg"]),
                    max_weight_kg=float(row["max_weight_kg"]),
                    min_age_months=int(row["min_age_months"]),
                    max_age_months=int(row["max_age_months"]),
                    size_group=normalize_text(row["size_group"]),
                    allowed_categories=allowed_categories,
                )
            except Exception as exc:
                row_number = idx + 2
                raise ValueError(
                    f"Fila invalida en reglas de raza (linea {row_number}) en '{file_path}'."
                ) from exc

        return bread_rules

    @staticmethod
    def read_dogs_records(file_path: str) -> list[DogRecord]:
        try:
            df = pd.read_csv(file_path)
        except Exception as exc:
            raise RuntimeError(f"No se pudo leer el archivo de registros: '{file_path}'") from exc
        CSVReaderService._assert_required_columns(df, CSVReaderService.DOG_RECORDS_REQUIRED_COLUMNS, file_path)

        records: list[DogRecord] = []
        has_registration_notes = "registration_notes" in df.columns
        for idx, row in df.iterrows():
            try:
                image_path = "" if pd.isna(row["image_path"]) else normalize_text(row["image_path"])
                registration_notes = ""
                if has_registration_notes and not pd.isna(row["registration_notes"]):
                    registration_notes = normalize_text(row["registration_notes"])
                record = DogRecord(
                    dog_id=int(row["dog_id"]),
                    dog_name=normalize_text(row["dog_name"]),
                    breed=normalize_text(row["breed"]),
                    sex=normalize_text(row["sex"]),
                    age_months=int(row["age_months"]),
                    weight_kg=float(row["weight_kg"]),
                    owner_name=normalize_text(row["owner_name"]),
                    competition_category=normalize_text(row["competition_category"]),
                    vaccination_status=normalize_text(row["vaccination_status"]),
                    registration_date=normalize_text(row["registration_date"]),
                    image_path=image_path,
                    registration_notes=registration_notes,
                )
                records.append(record)
            except Exception as exc:
                row_number = idx + 2
                raise ValueError(
                    f"Fila invalida en registros de perros (linea {row_number}) en '{file_path}'."
                ) from exc

        return records
