def build_etl_narrative_prompt(summary_json: str, anomalies_preview: str) -> str:
    return (
        "Analiza la corrida ETL y usa solo la entrada.\n"
        "Limites: executive_summary<=80 palabras; main_issues<=4; "
        "recommendations<=4; risk_assessment=1 frase.\n"
        "Anomalias con formato [dog_id,dog_name,anomaly_type,issue_level,message].\n"
        f"summary={summary_json}\n"
        f"anomalies={anomalies_preview}"
    )
