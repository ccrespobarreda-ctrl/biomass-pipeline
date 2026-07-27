"""Extractor de la tabla 'Wood pellet freight indications' del Argus."""

from datetime import date

from ..schemas.argus import Freight
from .base import buscar_num, texto_pdf


def extraer(ruta_pdf: str, fecha_issue: date) -> Freight:
    t = texto_pdf(ruta_pdf)
    return Freight(
        fecha_issue=fecha_issue,
        aveiro_ara_eur_t=buscar_num(r"Aveiro-ARA 3500 €/t\s+([\d.]+)", t),
        aveiro_cph_eur_t=buscar_num(r"Aveiro-Copenhagen 3500 €/t\s+([\d.]+)", t),
        aveiro_hull_eur_t=buscar_num(r"Aveiro-Hull \(UK\) 3500 €/t\s+([\d.]+)", t),
        riga_ara_eur_t=buscar_num(r"Riga-ARA 5000 €/t\s+([\d.]+)", t),
        riga_cph_eur_t=buscar_num(r"Riga-Copenhagen 5000 €/t\s+([\d.]+)", t),
        riga_stockholm_eur_t=buscar_num(r"Riga-Stockholm 5000 €/t\s+([\d.]+)", t),
        mobile_ara_25kt_usd_t=buscar_num(r"Mobile-ARA 25000 \$/t\s+([\d.]+)", t),
        mobile_ara_45kt_usd_t=buscar_num(r"Mobile-ARA 45000 \$/t\s+([\d.]+)", t),
        savannah_ara_25kt_usd_t=buscar_num(r"Savannah-ARA 25000 \$/t\s+([\d.]+)", t),
        savannah_ara_45kt_usd_t=buscar_num(r"Savannah-ARA 45000 \$/t\s+([\d.]+)", t),
        vancouver_ara_45kt_usd_t=buscar_num(r"Vancouver-ARA 45000 \$/t\s+([\d.]+)", t),
    )
