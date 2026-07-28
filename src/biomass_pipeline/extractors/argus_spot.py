"""Extractor de la tabla SPOT del Argus (bloque 'within 90 days').

PLANTILLA para tablas de rejilla limpia.
"""

from datetime import date

from ..schemas.argus import SpotPellets
from .base import buscar_num, texto_pdf

# el cambio semanal puede ser un numero con signo (+0.10, -0.30) o 'nc' (sin cambio)
CAMBIO = r"(?:[+-][\d.]+|nc)"


def extraer(ruta_pdf: str, fecha_issue: date) -> SpotPellets:
    texto = texto_pdf(ruta_pdf)
    return SpotPellets(
        fecha_issue=fecha_issue,
        cif_nwe_usd_t=buscar_num(r"cif NWE \$/t\s+([\d.]+)", texto),
        fob_baltics_eur_t=buscar_num(r"fob Baltic €/t\s+([\d.]+)", texto),
        fob_portugal_eur_t=buscar_num(r"fob Portugal €/t\s+([\d.]+)", texto),
        chips_cif_nwe_eur_gj=buscar_num(
            rf"cif NWE\s+([\d.]+)\s+{CAMBIO}\s+[\d.]+\s+[\d.]+\s+[\d.]+", texto
        ),
    )
