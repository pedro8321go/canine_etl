def normalize_text(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip()