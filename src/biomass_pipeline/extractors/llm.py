"""Extraccion con la API de Claude, SOLO para tablas que pdfplumber no logre parsear
(cabeceras apiladas, celdas fusionadas). Las tablas limpias no pasan por aqui.

Devuelve JSON validado contra un esquema Pydantic: nunca texto libre.
Requiere el extra 'llm' (pip install -e '.[llm]') y la credencial ANTHROPIC_API_KEY
inyectada desde el gestor de secretos.
"""

from __future__ import annotations

import json
import os

from pydantic import BaseModel


def extraer_con_llm[T: BaseModel](texto_tabla: str, esquema: type[T]) -> T:
    """Pide a Claude que rellene 'esquema' a partir del texto de la tabla."""
    from anthropic import Anthropic  # import perezoso: solo si se usa

    cliente = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    instruccion = (
        "Extrae los datos de esta tabla y devuelve SOLO un JSON que valide contra "
        f"este esquema (sin texto adicional):\n{esquema.model_json_schema()}\n\n"
        f"Tabla:\n{texto_tabla}"
    )
    resp = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": instruccion}],
    )
    crudo = "".join(b.text for b in resp.content if b.type == "text")
    crudo = crudo.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return esquema.model_validate(json.loads(crudo))
