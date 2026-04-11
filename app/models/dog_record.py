from dataclasses import dataclass

@dataclass
class DogRecord:
    dog_id: int
    dog_name: str
    breed: str
    sex: str
    age_months: int
    weight_kg: float
    owner_name: str
    competition_category: str
    vaccination_status: str
    registration_date: str
    image_path: str