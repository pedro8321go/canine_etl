from datetime import datetime
from time import perf_counter

from app.core.config import (
    ANOMALIES_REPORT_FILE,
    BREED_RULES_FILE,
    DOG_REGISTRATIONS_FILE,
    EXECUTION_SUMMARY_FILE,
    SQLITE_DB_FILE, PIPELINE_NAME, EXECUTION_NARRATIVE_FILE,
)
from app.core.logger import get_logger
from app.models.etl_execution import ETLExecution
from app.services.csv_reader import CSVReaderService
from app.services.narrative_service import NarrativeService
from app.services.report_generator import ReportGeneratorService
from app.services.status_service import StatusService
from app.services.validator import ValidatorService
from app.services.sqlite_loader import SQLiteLoaderService
from app.services.summary_service import SummaryService

logger = get_logger(__name__)


def main() -> None:
    execution_started_at = datetime.now().isoformat()
    timer_start = perf_counter()

    logger.info("Leyendo catálogo de razas...")
    breed_rules = CSVReaderService.read_breed_rules(BREED_RULES_FILE)

    logger.info("Leyendo registros de perros...")
    dog_records = CSVReaderService.read_dogs_records(DOG_REGISTRATIONS_FILE)

    logger.info("Validando registros...")
    validator = ValidatorService()
    anomalies = validator.validate_records(dog_records, breed_rules)

    logger.info("Calculando estado final por registro...")
    record_results = StatusService.build_record_results(dog_records, anomalies)

    logger.info("Construyendo resumen de ejecución...")
    summary = SummaryService.build_summary(len(dog_records), anomalies, record_results)

    execution_finished_at = datetime.now().isoformat()
    duration_seconds = perf_counter() - timer_start

    execution = ETLExecution(
        pipeline_name=PIPELINE_NAME,
        execution_started_at=execution_started_at,
        execution_finished_at=execution_finished_at,
        duration_seconds=duration_seconds,
        processed_records=len(dog_records),
    )

    logger.info("Generando reporte de salida...")
    ReportGeneratorService.generate_anomalies_csv(anomalies, ANOMALIES_REPORT_FILE)
    ReportGeneratorService.generate_execution_summary(summary, EXECUTION_SUMMARY_FILE)

    narrative_text = NarrativeService.build_narrative(summary, execution)
    NarrativeService.save_narrative(narrative_text, EXECUTION_NARRATIVE_FILE)

    logger.info("Cargando resultados en BD...")
    sqlite_loader = SQLiteLoaderService(SQLITE_DB_FILE)
    sqlite_loader.initialize_database()
    sqlite_loader.clear_previous_data()
    sqlite_loader.load_dog_records(dog_records, record_results)
    sqlite_loader.load_anomalies(anomalies)
    sqlite_loader.load_execution_summary(summary)
    sqlite_loader.load_etl_execution(execution)

    logger.info("Proceso finalizado.")
    logger.info(f"Pipeline: {execution.pipeline_name}")
    logger.info(f"Duración: {execution.duration_seconds:.4f} segundos")
    logger.info(f"Total de registros: {summary.total_records}")
    logger.info(f"Registros válidos: {summary.valid_records}")
    logger.info(f"Registros válidos con warnings: {summary.valid_with_warnings_records}")
    logger.info(f"Registros inválidos: {summary.invalid_records}")
    logger.info(f"Total de anomalías: {summary.total_anomalies}")
    logger.info(f"Errores: {summary.total_errors}")
    logger.info(f"Warnings: {summary.total_warnings}")
    logger.info(f"Reporte CSV: {ANOMALIES_REPORT_FILE}")
    logger.info(f"Resumen JSON: {EXECUTION_SUMMARY_FILE}")
    logger.info(f"Resumen narrativo: {EXECUTION_NARRATIVE_FILE}")
    logger.info(f"Base SQLite: {SQLITE_DB_FILE}")


if __name__ == "__main__":
    main()
