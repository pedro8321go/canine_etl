from app.core.config import (
    ANOMALIES_REPORT_FILE,
    BREED_RULES_FILE,
    DOG_REGISTRATIONS_FILE,
)
from app.core.logger import get_logger
from app.services.csv_reader import CSVReaderService
from app.services.report_generator import ReportGeneratorService
from app.services.validator import ValidatorService

logger = get_logger(__name__)


def main() -> None:
    logger.info("Leyendo catálogo de razas...")
    breed_rules = CSVReaderService.read_breed_rules(BREED_RULES_FILE)

    logger.info("Leyendo registros de perros...")
    dog_records = CSVReaderService.read_dogs_records(DOG_REGISTRATIONS_FILE)

    logger.info("Validando registros...")
    validator = ValidatorService()
    anomalies = validator.validate_records(dog_records, breed_rules)

    logger.info(f"Total de registros leídos: {len(dog_records)}")
    logger.info(f"Total de anomalías detectadas: {len(anomalies)}")

    logger.info("Generando reporte de anomalías...")
    ReportGeneratorService.generate_anomalies_csv(anomalies, ANOMALIES_REPORT_FILE)

    logger.info(f"Reporte generado en: {ANOMALIES_REPORT_FILE}")


if __name__ == "__main__":
    main()
