import csv
from pathlib import Path

from app.models.anomaly import Anomaly

class ReportGeneratorService:
    @staticmethod
    def generate_anomalies_csv(anomalies: list[Anomaly], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["dog_id", "dog_name", "anomaly_type", "severity", "message"])

            for anomaly in anomalies:
                writer.writerow([
                    anomaly.dog_id,
                    anomaly.dog_name,
                    anomaly.anomaly_type,
                    anomaly.severity,
                    anomaly.message,
                ])