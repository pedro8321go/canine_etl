import json
import sqlite3
from pathlib import Path

from app.models.anomaly import Anomaly
from app.models.dog_record import DogRecord
from app.models.dog_record_result import DogRecordResult
from app.models.etl_execution import ETLExecution
from app.models.execution_summary import ExecutionSummary


class SQLiteLoaderService:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def initialize_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dog_records (
                    dog_id INTEGER PRIMARY KEY,
                    dog_name TEXT NOT NULL,
                    breed TEXT NOT NULL,
                    sex TEXT NOT NULL,
                    age_months INTEGER NOT NULL,
                    weight_kg REAL NOT NULL,
                    owner_name TEXT NOT NULL,
                    competition_category TEXT NOT NULL,
                    vaccination_status TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    image_path TEXT,
                    record_status TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dog_id INTEGER NOT NULL,
                    dog_name TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    issue_level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_records INTEGER NOT NULL,
                    total_anomalies INTEGER NOT NULL,
                    total_errors INTEGER NOT NULL,
                    total_warnings INTEGER NOT NULL,
                    affected_records INTEGER NOT NULL,
                    valid_records INTEGER NOT NULL,
                    valid_with_warnings_records INTEGER NOT NULL,
                    invalid_records INTEGER NOT NULL,
                    anomaly_count_by_type TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etl_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    execution_started_at TEXT NOT NULL,
                    execution_finished_at TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    processed_records INTEGER NOT NULL
                )
            """)

            conn.commit()

    def clear_previous_data(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dog_records")
            cursor.execute("DELETE FROM anomalies")
            cursor.execute("DELETE FROM execution_summary")
            cursor.execute("DELETE FROM etl_executions")
            conn.commit()

    def load_dog_records(
        self,
        records: list[DogRecord],
        record_results: list[DogRecordResult],
    ) -> None:
        status_by_id = {result.dog_id: result.record_status for result in record_results}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.executemany("""
                INSERT INTO dog_records (
                    dog_id, dog_name, breed, sex, age_months, weight_kg,
                    owner_name, competition_category, vaccination_status,
                    registration_date, image_path, record_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    record.dog_id,
                    record.dog_name,
                    record.breed,
                    record.sex,
                    record.age_months,
                    record.weight_kg,
                    record.owner_name,
                    record.competition_category,
                    record.vaccination_status,
                    record.registration_date,
                    record.image_path,
                    status_by_id.get(record.dog_id, "invalid"),
                )
                for record in records
            ])

            conn.commit()

    def load_anomalies(self, anomalies: list[Anomaly]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.executemany("""
                INSERT INTO anomalies (
                    dog_id, dog_name, anomaly_type, issue_level, message
                ) VALUES (?, ?, ?, ?, ?)
            """, [
                (
                    anomaly.dog_id,
                    anomaly.dog_name,
                    anomaly.anomaly_type,
                    anomaly.issue_level,
                    anomaly.message,
                )
                for anomaly in anomalies
            ])

            conn.commit()

    def load_execution_summary(self, summary: ExecutionSummary) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO execution_summary (
                    total_records, total_anomalies, total_errors, total_warnings,
                    affected_records, valid_records, valid_with_warnings_records,
                    invalid_records, anomaly_count_by_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary.total_records,
                summary.total_anomalies,
                summary.total_errors,
                summary.total_warnings,
                summary.affected_records,
                summary.valid_records,
                summary.valid_with_warnings_records,
                summary.invalid_records,
                json.dumps(summary.anomaly_count_by_type, ensure_ascii=False),
            ))

            conn.commit()

    def load_etl_execution(self, execution: ETLExecution) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO etl_executions (
                    pipeline_name, execution_started_at, execution_finished_at,
                    duration_seconds, processed_records
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                execution.pipeline_name,
                execution.execution_started_at,
                execution.execution_finished_at,
                execution.duration_seconds,
                execution.processed_records,
            ))

            conn.commit()