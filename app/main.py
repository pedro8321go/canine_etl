from app.core.config import (
    ANOMALIES_REPORT_FILE,
    BREED_RULES_FILE,
    DOG_REGISTRATIONS_FILE,
    EXECUTION_SUMMARY_FILE,
    SQLITE_DB_FILE,
)
from app.core.logger import get_logger
from app.services.csv_reader import CSVReaderService
from app.services.report_generator import ReportGeneratorService
from app.services.validator import ValidatorService
from app.services.sqlite_loader import SQLiteLoaderService
from app.services.summary_service import SummaryService

logger = get_logger(__name__)


def main() -> None:
    logger.info("Leyendo catálogo de razas...")
    breed_rules = CSVReaderService.read_breed_rules(BREED_RULES_FILE)

    logger.info("Leyendo registros de perros...")
    dog_records = CSVReaderService.read_dogs_records(DOG_REGISTRATIONS_FILE)

    logger.info("Validando registros...")
    validator = ValidatorService()
    anomalies = validator.validate_records(dog_records, breed_rules)

    logger.info("Construyendo resumen de ejecución...")
    summary = SummaryService.build_summary(len(dog_records), anomalies)

    logger.info("Generando reporte de salida...")
    ReportGeneratorService.generate_anomalies_csv(anomalies, ANOMALIES_REPORT_FILE)
    ReportGeneratorService.generate_execution_summary(summary, EXECUTION_SUMMARY_FILE)

    logger.info("Cargando resultados en BD...")
    sqlite_loader = SQLiteLoaderService(SQLITE_DB_FILE)
    sqlite_loader.initialize_database()
    sqlite_loader.clear_previous_data()
    sqlite_loader.load_dog_records(dog_records)
    sqlite_loader.load_anomalies(anomalies)
    sqlite_loader.load_execution_summary(summary)

    logger.info("Proceso finalizado.")
    logger.info(f"Total de registros: {summary.total_records}")
    logger.info(f"Total de anomalías: {summary.total_anomalies}")
    logger.info(f"Errores: {summary.total_errors}")
    logger.info(f"Warnings: {summary.total_warnings}")
    logger.info(f"Registros afectados: {summary.affected_records}")
    logger.info(f"Reporte CSV: {ANOMALIES_REPORT_FILE}")
    logger.info(f"Resumen JSON: {EXECUTION_SUMMARY_FILE}")
    logger.info(f"Base SQLite: {SQLITE_DB_FILE}")


if __name__ == "__main__":
    main()
