from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ExecutionSummary:
    total_records: int
    total_anomalies: int
    total_errors: int
    total_warnings: int
    affected_records: int
    valid_records: int
    valid_with_warnings_records: int
    invalid_records: int
    anomaly_count_by_type: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)