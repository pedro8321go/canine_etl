# canine_etl

ETL de registros caninos para competencia, con validaciones determinísticas y validaciones asistidas por LLM (Cerebras), generación de reportes y carga en SQLite.

## Qué hace el proyecto

Procesa registros de perros desde CSV, valida calidad de datos, genera salidas analíticas y persiste resultados en base de datos.

Flujo principal:
1. Carga catálogo de razas (`breed_rules.csv`) y registros (`dogs_registrations.csv`).
2. Corrección opcional por LLM de razas no reconocidas (ej. `Pudel` -> `Poodle`).
3. Validaciones determinísticas (reglas de negocio).
4. Validación semántica asistida por LLM entre:
   - `breed`
   - `weight_kg`
   - `competition_category`
   - `registration_notes`
5. Cálculo de estado por registro y resumen de ejecución.
6. Generación de narrativa base y narrativa LLM.
7. Exportación de reportes y percistencia de la data en SQLite.

## Alcance

Incluye:
- Ingesta CSV para reglas y registros.
- Validación de:
  - existencia de raza
  - sexo
  - vacunación
  - imagen
  - duplicados
  - rango de edad por raza
  - rango de peso por raza
  - categoría permitida por raza
  - coherencia fecha de inscripción vs edad:
    - formato `YYYY-MM-DD`
    - no futura
    - no anterior a la edad declarada
- Corrección LLM de raza inválida a raza permitida.
- Validación semántica LLM con filtro determinístico para reducir falsos positivos.
- Persistencia en SQLite y reportes en `data/processed`.

## Límites actuales

- La validación semántica depende de un LLM externo y puede variar entre corridas.
- Las respuestas LLM pueden fallar o venir incompletas; el pipeline intenta tolerarlo, pero no garantiza 100%.
- La exactitud semántica depende de la calidad de `registration_notes`.

## Estructura de datos de entrada

### `data/raw/breed_rules.csv`
Columnas esperadas:
- `breed`
- `min_weight_kg`
- `max_weight_kg`
- `min_age_months`
- `max_age_months`
- `size_group`
- `allowed_categories` (separadas por `|`)

### `data/raw/dogs_registrations.csv`
Columnas esperadas:
- `dog_id`
- `dog_name`
- `breed`
- `sex`
- `age_months`
- `weight_kg`
- `owner_name`
- `competition_category`
- `vaccination_status`
- `registration_date` (`YYYY-MM-DD`)
- `image_path`
- `registration_notes` (texto libre para validación semántica)

## Salidas

Se generan en `data/processed`:
- `anomalies_report.csv`
- `execution_summary.json`
- `execution_narrative.txt`
- `llm_summary.json`
- `competition.db`

Tablas principales en SQLite:
- `dog_records`
- `anomalies`
- `execution_summary`
- `etl_executions`

## Requisitos

- Python 3.11+ (recomendado)
- Dependencias en `requirements.txt`

Instalación:
```bash
pip install -r requirements.txt
```

## Configuración

Usa archivo `.env` en la raíz:
```env
CEREBRAS_API_KEY=tu_api_key
CEREBRAS_MODEL=llama3.1-8b
```

Notas:
- Sin `CEREBRAS_API_KEY`, las partes LLM fallarán.
- El pipeline no se detiene por fallos de ciertas etapas LLM; registra warning y continúa en esos bloques.

## Ejecución

Desde la raíz del proyecto:
```bash
python app/main.py
```

## Tipos de anomalías relevantes

Determinísticas (ejemplos):
- `raza_no_válida`
- `peso_fuera_de_rango`
- `categoría_no_válida`
- `registro_duplicado`
- `fecha_inscripcion_formato_invalido`
- `fecha_inscripcion_futura`
- `fecha_inscripcion_incompatible_edad`

LLM (ejemplos):
- `raza_corregida_llm`
- `llm_semantic_*` (según `issue_type` devuelto por el modelo)

## Coste y rendimiento

- El costo de tokens proviene de:
  - corrección de razas LLM
  - validación semántica LLM
  - resumen narrativo LLM
- La validación semántica se procesa por lotes para reducir riesgo de respuesta truncada.

## Operación recomendada

1. Verificar formato y columnas de CSV antes de ejecutar.
2. Revisar `anomalies_report.csv` después de cada corrida.
3. Auditar anomalías `llm_semantic_*` cuando impacten decisiones.
4. Si necesitas ejecutar sin costo LLM, comenta temporalmente bloques en `app/main.py`.

