import csv
import json
from pathlib import Path

from app.models.anomaly import Anomaly
from app.models.execution_summary import ExecutionSummary


class ReportGeneratorService:
    @staticmethod
    def generate_anomalies_csv(anomalies: list[Anomaly], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["dog_id", "dog_name", "anomaly_type", "issue_level", "message"])

            for anomaly in anomalies:
                writer.writerow([
                    anomaly.dog_id,
                    anomaly.dog_name,
                    anomaly.anomaly_type,
                    anomaly.issue_level,
                    anomaly.message,
                ])

    @staticmethod
    def generate_execution_summary(summary: ExecutionSummary, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding="utf-8") as file:
            json.dump(summary.to_dict(), file, ensure_ascii=False, indent=2)