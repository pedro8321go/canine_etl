from pathlib import Path

from app.models.execution_summary import ExecutionSummary
from app.models.etl_execution import ETLExecution


class NarrativeService:
    @staticmethod
    def build_narrative(summary: ExecutionSummary, execution: ETLExecution) -> str:
        lines = [
            "Resumen narrativo de la ejecución ETL",
            f"Pipeline ejecutado: {execution.pipeline_name}.",
            f"Inicio de ejecución: {execution.execution_started_at}.",
            f"Fin de ejecución: {execution.execution_finished_at}.",
            f"Duración total: {execution.duration_seconds:.4f} segundos.",
            f"Registros procesados: {summary.total_records}.",
            f"Registros válidos: {summary.valid_records}.",
            f"Registros válidos con advertencias: {summary.valid_with_warnings_records}.",
            f"Registros inválidos: {summary.invalid_records}.",
            f"Total de anomalías detectadas: {summary.total_anomalies}.",
            f"Errores: {summary.total_errors}.",
            f"Warnings: {summary.total_warnings}.",
            f"Registros afectados por alguna incidencia: {summary.affected_records}.",
            "Distribución por tipo de anomalía:"
        ]

        for anomaly_type, count in summary.anomaly_count_by_type.items():
            lines.append(f"- {anomaly_type}: {count}")

        lines.append(
            "Este texto está preparado para ser usado como contexto de entrada en una integración con un modelo de lenguaje."
        )

        return "\n".join(lines)

    @staticmethod
    def save_narrative(text: str, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(text, encoding="utf-8")