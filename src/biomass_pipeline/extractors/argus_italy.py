"""Extractor del premium residencial de Italia ('European premium wood pellets').

Guardamos el valor Mid. Exigimos Mid+Low+High+cambio para no confundir con la
sub-tabla de indice mensual (que solo trae 3 numeros).
"""

from datetime import date

from ..schemas.argus import ItalyPremium
from .base import buscar_num, texto_pdf

CAMBIO = r"(?:[+-]?[\d.]+|nc)"  # cambio: +, -, sin signo, o 'nc'


def extraer(ruta_pdf: str, fecha_issue: date) -> ItalyPremium:
    t = texto_pdf(ruta_pdf)
    return ItalyPremium(
        fecha_issue=fecha_issue,
        bulk_mid_eur_t=buscar_num(rf"Bulk\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+{CAMBIO}", t),
        bagged_mid_eur_t=buscar_num(rf"Bagged\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+{CAMBIO}", t),
    )
