"""Extractor de la tabla 'Biomass prices' del FEM (PLANTILLA de tabla mensual).

Clave: NO fija posiciones de columna. Lee la cabecera para localizar el mes mas
reciente, asi sobrevive a que las columnas cambien en cada issue
(Jan-25 -> Feb-25 -> ... -> Jun-26).
"""

import re
from datetime import date

import pdfplumber

from ..schemas.fem import BiomassPricesFEM

# la tabla esta en la pagina 3 (indice 2)
PAGINA_TABLA = 2


def _texto_pagina(ruta_pdf: str, pag: int = PAGINA_TABLA) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        return pdf.pages[pag].extract_text() or ""


def _indice_mes_reciente(texto: str) -> int | None:
    """Cuenta las columnas de periodo de la cabecera; el mes reciente es la ultima."""
    for line in texto.split("\n"):
        if "chg on" in line:
            periodos = re.findall(r"[0-9]Q\d{2}|[A-Z][a-z]{2}-\d{2}", line)
            return len(periodos) - 1
    return None


def _valor_fila(texto: str, etiqueta: str, unidad: str, idx: int) -> float | None:
    """Valor de 'etiqueta' en 'unidad', columna idx. Ignora la etiqueta cortando
    la linea a partir de la unidad (evita capturar el guion del nombre)."""
    lineas = texto.split("\n")
    for i, line in enumerate(lineas):
        if etiqueta in line:
            for j in range(i, min(i + 3, len(lineas))):
                if unidad in lineas[j]:
                    resto = lineas[j].split(unidad, 1)[1]
                    nums = re.findall(r"-?\d+\.\d+|(?<= )-(?= )", resto)
                    if len(nums) > idx and nums[idx] != "-":
                        return float(nums[idx])
    return None


def extraer(ruta_pdf: str, mes: date) -> BiomassPricesFEM:
    texto = _texto_pagina(ruta_pdf)
    idx = _indice_mes_reciente(texto)
    if idx is None:
        raise ValueError("no se encontro la cabecera de periodos en la tabla del FEM")
    return BiomassPricesFEM(
        mes=mes,
        germany_depi_eur_t=_valor_fila(texto, "Heating wood pellets - Germany", "€/tonne", idx),
        austria_propellet_eur_t=_valor_fila(
            texto, "Heating wood pellets - Austria", "€/tonne", idx
        ),
        swiss_preis_eur_t=_valor_fila(texto, "Heating wood pellets - Switzerland", "€/tonne", idx),
        baltpool_eur_t=_valor_fila(texto, "Heating wood pellets - Lithuania", "€/tonne", idx),
    )
