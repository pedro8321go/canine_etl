import pandas as pd
from app.models.breed_rule import BreedRule
from app.models.dog_record import DogRecord
from app.utils.text_normalizer import normalize_text

class CSVReaderService:
    @staticmethod
    def read_breed_rules(file_path: str) -> dict[str, BreedRule]:
        df = pd.read_csv(file_path)
        bread_rules: dict[str, BreedRule] = {}
        for _, row in df.iterrows():
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

        return bread_rules

    @staticmethod
    def read_dogs_records(file_path: str) -> list[DogRecord]:
        df = pd.read_csv(file_path)
        records: list[DogRecord] = []
        for _, row in df.iterrows():
            image_path = "" if pd.isna(row["image_path"]) else normalize_text(row["image_path"])
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
            )
            records.append(record)

        return records