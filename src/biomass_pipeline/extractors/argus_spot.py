"""Extractor de la tabla SPOT del Argus (bloque 'within 90 days').

Es la PLANTILLA para el resto de tablas: copia este patron, cambia el esquema
y los patrones regex, y tienes un extractor nuevo.
"""
from datetime import date

from ..schemas.argus import SpotPellets
from .base import buscar_num, texto_pdf


def extraer(ruta_pdf: str, fecha_issue: date) -> SpotPellets:
    texto = texto_pdf(ruta_pdf)
    return SpotPellets(
        fecha_issue=fecha_issue,
        cif_nwe_usd_t=buscar_num(r"cif NWE \$/t\s+([\d.]+)", texto),
        fob_baltics_eur_t=buscar_num(r"fob Baltic €/t\s+([\d.]+)", texto),
        fob_portugal_eur_t=buscar_num(r"fob Portugal €/t\s+([\d.]+)", texto),
        # el signo del cambio puede ser + o -; exigimos los 3 indices de mes para desambiguar
        chips_cif_nwe_eur_gj=buscar_num(
            r"cif NWE\s+([\d.]+)\s+[+-][\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+", texto
        ),
    )
