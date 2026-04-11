from collections import Counter

from app.models.anomaly import Anomaly
from app.models.execution_summary import ExecutionSummary

class SummaryService:
    @staticmethod
    def build_summary(total_records: int, anomalies: list[Anomaly]) -> ExecutionSummary:
        anomaly_counter = Counter(anomaly.anomaly_type for anomaly in anomalies)
        affected_records = len({anomaly.dog_id for anomaly in anomalies})
        total_errors = sum(1 for anomaly in anomalies if anomaly.issue_level == "error")
        total_warnings = sum(1 for anomaly in anomalies if anomaly.issue_level == "warning")

        return ExecutionSummary(
            total_records=total_records,
            total_anomalies=len(anomalies),
            total_errors=total_errors,
            total_warnings=total_warnings,
            affected_records=affected_records,
            anomaly_count_by_type=dict(anomaly_counter),
        )
