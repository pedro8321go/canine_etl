from dataclasses import dataclass

@dataclass
class DogRecordResult:
    dog_id: int
    dog_name: str
    record_status: str