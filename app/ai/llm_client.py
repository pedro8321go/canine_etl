import json
import os
import time
from typing import Any

import cerebras.cloud.sdk
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("Cerebras API key is required")

        self.model = os.getenv("CEREBRAS_MODEL", "llama3.1-8b")
        self.client = Cerebras(api_key=api_key)

    def generate_structured_json(
        self,
        prompt: str,
        json_schema: dict[str, Any],
        max_output_tokens: int = 600,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Responde en espanol. Solo JSON valido."},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=max_output_tokens,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": json_schema["name"],
                            "strict": True,
                            "schema": json_schema["schema"],
                        },
                    },
                )

                text_output = completion.choices[0].message.content
                if not text_output:
                    raise RuntimeError("Cerebras no devolvio contenido en texto.")

                return json.loads(text_output)

            except cerebras.cloud.sdk.APIError as exc:
                last_error = RuntimeError(f"APIError en Cerebras: {exc}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise RuntimeError(
                        f"Error al generar salida estructurada con Cerebras: {last_error}"
                    ) from exc
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                else:
                    raise RuntimeError(
                        f"Error al generar salida estructurada con Cerebras: {exc}"
                    ) from exc

        raise RuntimeError(f"Fallo inesperado en generate_structured_json: {last_error}")
