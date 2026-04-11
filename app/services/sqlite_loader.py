import sqlite3
from pathlib import Path

from app.models.execution_summary import ExecutionSummary
from app.models.anomaly import Anomaly
from app.models.dog_record import DogRecord

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
                    image_path TEXT
                )
            """)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS anomalies
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               dog_id INTEGER NOT NULL,
                               dog_name TEXT NOT NULL,
                               anomaly_type TEXT NOT NULL,
                               issue_level TEXT NOT NULL,
                               message TEXT NOT NULL
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS execution_summary
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               total_records INTEGER NOT NULL,
                               total_anomalies INTEGER NOT NULL,
                               total_errors INTEGER NOT NULL,
                               total_warnings INTEGER NOT NULL,
                               affected_records INTEGER NOT NULL,
                               anomaly_count_by_type TEXT NOT NULL
                           )
                           """)

            conn.commit()

    def clear_previous_data(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dog_records")
            cursor.execute("DELETE FROM anomalies")
            cursor.execute("DELETE FROM execution_summary")
            conn.commit()

    def load_dog_records(self, records: list[DogRecord]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.executemany("""
                               INSERT INTO dog_records (dog_id, dog_name, breed, sex, age_months, weight_kg,
                                                        owner_name, competition_category, vaccination_status,
                                                        registration_date, image_path)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                                   )
                                   for record in records
                               ])

            conn.commit()

    def load_anomalies(self, anomalies: list[Anomaly]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.executemany("""
                               INSERT INTO anomalies (dog_id, dog_name, anomaly_type, issue_level, message)
                               VALUES (?, ?, ?, ?, ?)
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
        import json

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO execution_summary (total_records, total_anomalies, total_errors,
                                                          total_warnings, affected_records, anomaly_count_by_type)
                           VALUES (?, ?, ?, ?, ?, ?)
                           """, (
                               summary.total_records,
                               summary.total_anomalies,
                               summary.total_errors,
                               summary.total_warnings,
                               summary.affected_records,
                               json.dumps(summary.anomaly_count_by_type, ensure_ascii=False),
                           ))

            conn.commit()

