"""Extractor de la tabla 'Asian palm kernel shells' del Argus.

La tabla tiene DOS secciones, en este orden en el PDF:
    Excl. to Japan FIT   -> Sumatra / Malaysia SIN prima FIT   (cols BP, BR)
    To Japan FIT         -> Sumatra / Malaysia CON prima FIT   (cols BO, BQ)

Cada seccion se delimita por su encabezado:
  - 'Excl. to Japan FIT' va desde ese texto hasta 'To Japan FIT'.
  - 'To Japan FIT' va desde ese texto en adelante.
Cada fila se busca DENTRO de su seccion, asi que si una fila falta en su seccion
(Argus a veces no publica un precio) el resultado es NULL limpio, sin robar el
valor de la otra seccion.

OJO: 'Excl. to Japan FIT' CONTIENE el texto 'to Japan FIT'. Para partir usamos el
encabezado 'To Japan FIT' con T mayuscula, que solo aparece en la 2a seccion.
"""

from datetime import date

from ..schemas.argus import PalmKernelShells
from .base import buscar_num, texto_pdf

CAMBIO = r"(?:[+-][\d.]+|nc)"
RE_SUMATRA = rf"fob east coast Sumatra\s+([\d.]+)\s+{CAMBIO}"
RE_MALAYSIA = rf"fob peninsular Malaysia\s+([\d.]+)\s+{CAMBIO}"

MARCA_EXCL = "Excl. to Japan FIT"
MARCA_FIT = "To Japan FIT"


def _seccion_excl(t: str) -> str:
    """Trozo entre 'Excl. to Japan FIT' y 'To Japan FIT'. Vacio si falta el encabezado."""
    ini = t.find(MARCA_EXCL)
    if ini == -1:
        return ""
    fin = t.find(MARCA_FIT, ini + len(MARCA_EXCL))
    return t[ini:fin] if fin != -1 else t[ini:]


def _seccion_fit(t: str) -> str:
    """Trozo desde 'To Japan FIT' en adelante. Vacio si falta el encabezado."""
    ini = t.find(MARCA_FIT, t.find(MARCA_EXCL) + 1) if MARCA_EXCL in t else t.find(MARCA_FIT)
    return t[ini:] if ini != -1 else ""


def extraer(ruta_pdf: str, fecha_issue: date) -> PalmKernelShells:
    t = texto_pdf(ruta_pdf)
    excl = _seccion_excl(t)
    fit = _seccion_fit(t)
    return PalmKernelShells(
        fecha_issue=fecha_issue,
        # con prima FIT (seccion 'To Japan FIT')
        sumatra_fit_usd_t=buscar_num(RE_SUMATRA, fit),
        malaysia_fit_usd_t=buscar_num(RE_MALAYSIA, fit),
        # sin prima FIT (seccion 'Excl. to Japan FIT')
        sumatra_usd_t=buscar_num(RE_SUMATRA, excl),
        malaysia_usd_t=buscar_num(RE_MALAYSIA, excl),
    )