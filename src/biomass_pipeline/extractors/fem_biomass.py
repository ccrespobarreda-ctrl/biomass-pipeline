"""Extractor de la tabla 'Biomass prices' del FEM.

extraer_todos() emite UNA fila por cada mes que reporta el issue. Asi, al cargarlas
en orden, los meses que un issue trae vacios se rellenan desde issues posteriores.
"""

import re
from datetime import date

import pdfplumber

from ..schemas.fem import BiomassPricesFEM

PAGINA_TABLA = 2
MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _texto_pagina(ruta_pdf: str, pag: int = PAGINA_TABLA) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        return pdf.pages[pag].extract_text() or ""


def _columnas(texto: str) -> list[str]:
    """Etiquetas de periodo de la cabecera (trimestrales + mensuales)."""
    for line in texto.split("\n"):
        if "chg on" in line:
            return re.findall(r"[0-9]Q\d{2}|[A-Z][a-z]{2}-\d{2}", line)
    return []


def _nums_fila(texto: str, etiqueta: str, unidad: str) -> list[str] | None:
    lineas = texto.split("\n")
    for i, line in enumerate(lineas):
        if etiqueta in line:
            for j in range(i, min(i + 3, len(lineas))):
                if unidad in lineas[j]:
                    return re.findall(r"-?\d+\.\d+|(?<= )-(?= )", lineas[j].split(unidad, 1)[1])
    return None


def _valor(texto: str, etiqueta: str, unidad: str, idx: int) -> float | None:
    nums = _nums_fila(texto, etiqueta, unidad)
    if nums and len(nums) > idx and nums[idx] != "-":
        return float(nums[idx])
    return None


def _mes_a_fecha(etiqueta: str) -> date:
    m = re.match(r"([A-Z][a-z]{2})-(\d{2})", etiqueta)
    return date(2000 + int(m.group(2)), MESES[m.group(1)], 1)


def extraer_todos(ruta_pdf: str, issue_origen: str) -> list[BiomassPricesFEM]:
    """Una fila por cada columna MENSUAL del issue (las trimestrales se ignoran)."""
    texto = _texto_pagina(ruta_pdf)
    cols = _columnas(texto)
    filas = []
    for idx, etiqueta in enumerate(cols):
        if not re.match(r"[A-Z][a-z]{2}-\d{2}", etiqueta):
            continue  # saltar columnas trimestrales (4Q23, 1Q25...)
        filas.append(
            BiomassPricesFEM(
                mes=_mes_a_fecha(etiqueta),
                issue_origen=issue_origen,
                germany_depi_eur_t=_valor(texto, "Heating wood pellets - Germany", "€/tonne", idx),
                austria_propellet_eur_t=_valor(
                    texto, "Heating wood pellets - Austria", "€/tonne", idx
                ),
                swiss_preis_eur_t=_valor(
                    texto, "Heating wood pellets - Switzerland", "€/tonne", idx
                ),
                baltpool_eur_t=_valor(texto, "Heating wood pellets - Lithuania", "€/tonne", idx),
                endex_ancla_eur_t=_valor(texto, "Industrial wood pellets", "€/tonne", idx),
                finland_eur_mwh=_valor(texto, "Forest biomass - Finland", "€/MWh", idx),
                sweden_eur_mwh=_valor(texto, "Energy wood/ biomass - Sweden", "€/MWh", idx),
                pine_pulpwood_usd=_valor(texto, "Pine pulpwood", "US$/s.ton", idx),
                pine_chips_usd=_valor(texto, "In-wood pine chips", "US$/s.ton", idx),
                pine_residuals_usd=_valor(texto, "Pine process residuals", "US$/s.ton", idx),
                lithuania_chips_eur_mwh=_valor(texto, "Wood chips - Lith", "€/MWh", idx),
            )
        )
    return filas


def extraer(ruta_pdf: str, mes=None, issue_origen: str = "") -> BiomassPricesFEM | None:
    """Compatibilidad: devuelve solo el mes mas reciente del issue.

    Para la carga real usa extraer_todos(), que emite todos los meses.
    """
    filas = extraer_todos(ruta_pdf, issue_origen)
    return filas[-1] if filas else None
