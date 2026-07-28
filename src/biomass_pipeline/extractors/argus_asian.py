"""Extractor de la tabla 'Asian industrial wood pellets' del Argus."""

from datetime import date

from ..schemas.argus import AsianPellets
from .base import buscar_num, texto_pdf

CAMBIO = r"(?:[+-][\d.]+|nc)"  # numero con signo o 'nc' (sin cambio)


def extraer(ruta_pdf: str, fecha_issue: date) -> AsianPellets:
    t = texto_pdf(ruta_pdf)
    return AsianPellets(
        fecha_issue=fecha_issue,
        viet_japan_fit_usd_t=buscar_num(rf"fob Vietnam to Japan FIT\s+([\d.]+)\s+{CAMBIO}", t),
        viet_korea_usd_t=buscar_num(rf"fob Vietnam to S Korea\s+([\d.]+)\s+{CAMBIO}", t),
        gwangyang_usd_t=buscar_num(rf"cfr Gwangyang\s+([\d.]+)\s+{CAMBIO}", t),
    )
