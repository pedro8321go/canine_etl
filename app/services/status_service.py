from app.models.anomaly import Anomaly
from app.models.dog_record import DogRecord
from app.models.dog_record_result import DogRecordResult

class StatusService:
    @staticmethod
    def build_record_results(
            dog_records: list[DogRecord],
            anomalies: list[Anomaly],
    ) -> list[DogRecordResult]:
        anomalies_by_dog: dict[int, list[Anomaly]] = {}

        for anomaly in anomalies:
            anomalies_by_dog.setdefault(anomaly.dog_id, []).append(anomaly)

        results: list[DogRecordResult] = []

        for record in dog_records:
            dog_anomalies = anomalies_by_dog.get(record.dog_id, [])

            if not dog_anomalies:
                status = "valid"
            elif any(anomaly.issue_level == "error" for anomaly in dog_anomalies):
                status = "invalid"
            else:
                status = "valid_with_warnings"

            results.append(
                DogRecordResult(
                    dog_id=record.dog_id,
                    dog_name=record.dog_name,
                    record_status=status,
                )
            )

        return results