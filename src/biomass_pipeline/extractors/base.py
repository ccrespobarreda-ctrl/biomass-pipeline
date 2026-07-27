"""Utilidades compartidas por todos los extractores.

El patron de cada extractor es siempre el mismo:
  1) leer el texto del PDF (pdfplumber),
  2) localizar los numeros con regex (o, si la tabla se resiste, con la API de Claude),
  3) devolver un objeto Pydantic validado (el contrato de salida).

Cuando una tabla NO se pueda parsear con regex, se usara extraer_con_llm()
(ver extractors/llm.py). Las tablas limpias no lo necesitan.
"""
import re

import pdfplumber


def texto_pdf(ruta_pdf: str) -> str:
    """Devuelve todo el texto del PDF concatenado por paginas."""
    with pdfplumber.open(ruta_pdf) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)


def buscar_num(patron: str, texto: str) -> float | None:
    """Primer numero que casa el patron, o None si no aparece."""
    m = re.search(patron, texto)
    return float(m.group(1)) if m else None
