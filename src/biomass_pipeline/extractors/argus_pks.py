"""Extractor de la tabla 'Asian palm kernel shells' del Argus (variante to Japan FIT)."""

from datetime import date

from ..schemas.argus import PalmKernelShells
from .base import buscar_num, texto_pdf

CAMBIO = r"(?:[+-][\d.]+|nc)"


def extraer(ruta_pdf: str, fecha_issue: date) -> PalmKernelShells:
    t = texto_pdf(ruta_pdf)
    return PalmKernelShells(
        fecha_issue=fecha_issue,
        sumatra_fit_usd_t=buscar_num(rf"fob east coast Sumatra\s+([\d.]+)\s+{CAMBIO}", t),
        malaysia_fit_usd_t=buscar_num(rf"fob peninsular Malaysia\s+([\d.]+)\s+{CAMBIO}", t),
    )
