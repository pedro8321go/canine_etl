from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

BASE_RULES_FILE = RAW_DATA_DIR / "breed_rules.csv"
DOG_REGISTRATIONS_FILE = BASE_RULES_FILE / "dog_registrations.csv"
ANOMALIES_REPORT_FILE = PROCESSED_DATA_DIR / "anomalies_report.csv"

VALID_VACCINATION_STATUES = {"Completo", "Incompleto", "Pendiente"}
VALID_SEX_VALUES = {"M", "F"}