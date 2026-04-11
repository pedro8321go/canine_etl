from dataclasses import dataclass

@dataclass
class Anomaly:
    dog_id: int
    dog_name: str
    anomaly_type: str
    issue_level: str
    message: str