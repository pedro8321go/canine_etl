from pathlib import Path

# app/core/config.py -> raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

BREED_RULES_FILE = RAW_DATA_DIR / "breed_rules.csv"
DOG_REGISTRATIONS_FILE = RAW_DATA_DIR / "dogs_registrations.csv"
ANOMALIES_REPORT_FILE = PROCESSED_DATA_DIR / "anomalies_report.csv"

VALID_VACCINATION_STATUES = {"Completo", "Incompleto", "Pendiente"}
VALID_SEX_VALUES = {"M", "H"}
