"""Extractor de la tabla 'Asian palm kernel shells' del Argus, variante 'To Japan FIT'.

La tabla tiene DOS secciones ('Excl. to Japan FIT' y 'To Japan FIT'). Nos quedamos
con la segunda: buscamos los precios solo en el texto que va DESPUES de ese encabezado.
"""

from datetime import date

from ..schemas.argus import PalmKernelShells
from .base import buscar_num, texto_pdf

CAMBIO = r"(?:[+-][\d.]+|nc)"


def extraer(ruta_pdf: str, fecha_issue: date) -> PalmKernelShells:
    t = texto_pdf(ruta_pdf)
    # quedarnos solo con la seccion 'To Japan FIT' (T mayuscula; 'Excl. to Japan FIT' va antes)
    idx = t.find("To Japan FIT")
    seccion = t[idx:] if idx != -1 else t
    return PalmKernelShells(
        fecha_issue=fecha_issue,
        sumatra_fit_usd_t=buscar_num(rf"fob east coast Sumatra\s+([\d.]+)\s+{CAMBIO}", seccion),
        malaysia_fit_usd_t=buscar_num(rf"fob peninsular Malaysia\s+([\d.]+)\s+{CAMBIO}", seccion),
    )