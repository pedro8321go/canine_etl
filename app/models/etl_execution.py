from dataclasses import dataclass

@dataclass
class ETLExecution:
    pipeline_name: str
    execution_started_at: str
    execution_finished_at: str
    duration_seconds: float
    processed_records: int