def build_etl_narrative_prompt(summary_json: str, anomalies_preview: str) -> str:
    return (
        "Analiza la corrida ETL y usa solo la entrada.\n"
        "Responde con tono ejecutivo y orientado a decision operativa.\n"
        "Formato esperado:\n"
        "- executive_summary: 1 parrafo breve (80-110 palabras), describiendo volumen procesado, "
        "estado general y tipos de errores criticos.\n"
        "- main_issues: 4-5 bullets, cada uno iniciando con 'Se detecto' o 'Existen' o 'Hay'.\n"
        "- recommendations: 4-5 acciones concretas en infinitivo (Corregir, Eliminar, Revisar, Validar, Solicitar).\n"
        "- risk_assessment: 1 frase iniciando con 'El riesgo operativo es ...' y justificando impacto.\n"
        "No inventes datos. Si un issue no aparece en la entrada, no lo incluyas.\n"
        "Anomalias con formato [dog_id,dog_name,anomaly_type,issue_level,message].\n"
        f"summary={summary_json}\n"
        f"anomalies={anomalies_preview}"
    )


def build_breed_correction_prompt(
    invalid_breeds_json: str,
    allowed_breeds_json: str,
) -> str:
    return (
        "Corrige nombres de raza escritos con errores.\n"
        "Usa solo razas permitidas. Si no hay sustitucion confiable, no reemplaces.\n"
        "Devuelve correcciones para cada source_breed de entrada.\n"
        f"invalid_breeds={invalid_breeds_json}\n"
        f"allowed_breeds={allowed_breeds_json}"
    )


def build_semantic_validation_prompt(
    records_json: str,
    allowed_breeds_json: str,
) -> str:
    return (
        "Evalua CADA registro y devuelve un item por cada dog_id recibido.\n"
        "Compara literalmente breed, weight_kg y competition_category contra registration_notes.\n"
        "Marca has_issue=true solo si hay contradiccion textual explicita.\n"
        "No usar inferencias blandas. No inventar datos.\n"
        "Reglas duras:\n"
        "1) Si la nota menciona un peso en kg y difiere claramente de weight_kg, has_issue=true (error).\n"
        "2) Si la nota menciona una categoria distinta a competition_category, has_issue=true (error).\n"
        "3) Si la nota menciona otra raza del catalogo permitida distinta a breed, has_issue=true (error).\n"
        "4) Si no hay contradiccion textual explicita, has_issue=false.\n"
        "Issue type sugeridos: semantic_weight_mismatch, semantic_category_mismatch, semantic_breed_mismatch.\n"
        "Mensaje breve y factual, citando el conflicto exacto.\n"
        f"records={records_json}\n"
        f"allowed_breeds={allowed_breeds_json}"
    )
