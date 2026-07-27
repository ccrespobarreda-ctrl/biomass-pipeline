"""Extractor de la tabla 'Asian industrial wood pellets' del Argus."""

from datetime import date

from ..schemas.argus import AsianPellets
from .base import buscar_num, texto_pdf


def extraer(ruta_pdf: str, fecha_issue: date) -> AsianPellets:
    t = texto_pdf(ruta_pdf)
    # el numero va seguido del cambio (+/-), lo que desambigua de las menciones en prosa
    return AsianPellets(
        fecha_issue=fecha_issue,
        viet_japan_fit_usd_t=buscar_num(r"fob Vietnam to Japan FIT\s+([\d.]+)\s+[+-]", t),
        viet_korea_usd_t=buscar_num(r"fob Vietnam to S Korea\s+([\d.]+)\s+[+-]", t),
        gwangyang_usd_t=buscar_num(r"cfr Gwangyang\s+([\d.]+)\s+[+-]", t),
    )
