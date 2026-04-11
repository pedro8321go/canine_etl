from dataclasses import dataclass

@dataclass
class BreedRule:
    breed: str
    min_weight_kg: float
    max_weight_kg: float
    min_age_months: int
    max_age_months: int
    size_group: str
    allowed_categories: list[str]