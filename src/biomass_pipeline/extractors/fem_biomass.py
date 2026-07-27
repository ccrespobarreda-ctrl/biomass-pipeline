"""Extractor de la tabla 'Biomass prices' del FEM (PLANTILLA de tabla mensual).

Clave: NO fija posiciones de columna. Lee la cabecera para localizar el mes mas
reciente, asi sobrevive a que las columnas cambien en cada issue.

Nota: pino, Suecia, Finlandia y chips de Lituania son series TRIMESTRALES; en las
columnas mensuales suelen venir '-', por lo que saldran null la mayoria de meses
(decision tomada: null cuando no hay dato). Si quisieras rellenarlas con el ultimo
valor disponible del issue, usa _valor_ultimo en vez de _valor_fila para esas filas.
"""

import re
from datetime import date

import pdfplumber

from ..schemas.fem import BiomassPricesFEM

PAGINA_TABLA = 2


def _texto_pagina(ruta_pdf: str, pag: int = PAGINA_TABLA) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        return pdf.pages[pag].extract_text() or ""


def _indice_mes_reciente(texto: str) -> int | None:
    for line in texto.split("\n"):
        if "chg on" in line:
            periodos = re.findall(r"[0-9]Q\d{2}|[A-Z][a-z]{2}-\d{2}", line)
            return len(periodos) - 1
    return None


def _nums_fila(texto: str, etiqueta: str, unidad: str) -> list[str] | None:
    """Lista de valores (numeros o '-') de la fila 'etiqueta' en 'unidad'."""
    lineas = texto.split("\n")
    for i, line in enumerate(lineas):
        if etiqueta in line:
            for j in range(i, min(i + 3, len(lineas))):
                if unidad in lineas[j]:
                    resto = lineas[j].split(unidad, 1)[1]
                    return re.findall(r"-?\d+\.\d+|(?<= )-(?= )", resto)
    return None


def _valor_fila(texto: str, etiqueta: str, unidad: str, idx: int) -> float | None:
    """Valor de la columna idx (mes reciente). None si no hay dato ese mes."""
    nums = _nums_fila(texto, etiqueta, unidad)
    if nums and len(nums) > idx and nums[idx] != "-":
        return float(nums[idx])
    return None


def _valor_ultimo(texto: str, etiqueta: str, unidad: str) -> float | None:
    """Ultimo valor NO vacio de la fila (util para series trimestrales)."""
    nums = _nums_fila(texto, etiqueta, unidad)
    if nums:
        for v in reversed(nums):
            if v != "-":
                return float(v)
    return None


def extraer(ruta_pdf: str, mes: date) -> BiomassPricesFEM:
    texto = _texto_pagina(ruta_pdf)
    idx = _indice_mes_reciente(texto)
    if idx is None:
        raise ValueError("no se encontro la cabecera de periodos en la tabla del FEM")
    return BiomassPricesFEM(
        mes=mes,
        # residenciales (mensuales)
        germany_depi_eur_t=_valor_fila(texto, "Heating wood pellets - Germany", "€/tonne", idx),
        austria_propellet_eur_t=_valor_fila(
            texto, "Heating wood pellets - Austria", "€/tonne", idx
        ),
        swiss_preis_eur_t=_valor_fila(texto, "Heating wood pellets - Switzerland", "€/tonne", idx),
        baltpool_eur_t=_valor_fila(texto, "Heating wood pellets - Lithuania", "€/tonne", idx),
        endex_ancla_eur_t=_valor_fila(texto, "Industrial wood pellets", "€/tonne", idx),
        # series trimestrales / best-effort (null cuando el mes reciente es '-')
        finland_eur_mwh=_valor_fila(texto, "Forest biomass - Finland", "€/MWh", idx),
        sweden_eur_mwh=_valor_fila(texto, "Energy wood/ biomass - Sweden", "€/MWh", idx),
        pine_pulpwood_usd=_valor_fila(texto, "Pine pulpwood", "US$/s.ton", idx),
        pine_chips_usd=_valor_fila(texto, "In-wood pine chips", "US$/s.ton", idx),
        pine_residuals_usd=_valor_fila(texto, "Pine process residuals", "US$/s.ton", idx),
        lithuania_chips_eur_mwh=_valor_fila(texto, "Wood chips - Lith", "€/MWh", idx),
    )
