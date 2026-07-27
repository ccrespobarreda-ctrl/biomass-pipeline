"""Extractor del premium residencial de Italia ('European premium wood pellets').

Guardamos el valor Mid. El patron exige Mid+Low+High+cambio para no confundirse
con la sub-tabla de indice mensual (que solo tiene 3 numeros).
"""

from datetime import date

from ..schemas.argus import ItalyPremium
from .base import buscar_num, texto_pdf


def extraer(ruta_pdf: str, fecha_issue: date) -> ItalyPremium:
    t = texto_pdf(ruta_pdf)
    return ItalyPremium(
        fecha_issue=fecha_issue,
        bulk_mid_eur_t=buscar_num(r"Bulk\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+-?[\d.]+", t),
        bagged_mid_eur_t=buscar_num(r"Bagged\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+-?[\d.]+", t),
    )
