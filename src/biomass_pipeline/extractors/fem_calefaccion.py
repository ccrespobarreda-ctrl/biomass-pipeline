"""Extractor de la pagina 'European Pellet Heating Economics' del FEM (P18).

Lee dos tablas:
  - 'Heating oil prices': precio del gasoleo de calefaccion por pais (EUR/litro; los
    issues de 2024 ponen '€/litre' en vez de 'EUR/litre').
  - 'Heating oil versus pellet price differential': ventaja del pellet frente al
    gasoleo, en % (Austria, Francia, Alemania).

Cada issue trae tres meses: el mismo mes del ano anterior, el mes pasado y el actual
(cabecera tipo 'Oct-25 Sep-26 Oct-26 M/M Y/Y'). Se emite una fila por (mes, pais).
Las columnas M/M e Y/Y se guardan tal cual las publica el FEM (las calcula con decimales que
no salen en la tabla, asi que recalcularlas puede dar una centesima distinta), solo en la
fila del mes actual del issue.

Francia: el FEM solo publica su diferencial del ano anterior; las columnas del mes
pasado y del actual vienen como '-' y se guardan vacias.

La pagina cambia de numero entre issues, asi que se busca por su titulo.
"""

import re
from datetime import date

import pdfplumber

from ..schemas.fem import CalefaccionFEM

TITULO_GASOLEO = "Heating oil prices"
TITULO_DIFERENCIAL = "Heating oil versus pellet price differential"
PAISES_GASOLEO = ("Austria", "Germany", "France", "Sweden", "Denmark", "Italy")
PAISES_DIFERENCIAL = ("Austria", "France", "Germany")
MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
RE_CABECERA = re.compile(r"^([A-Z][a-z]{2}-\d{2}) ([A-Z][a-z]{2}-\d{2}) ([A-Z][a-z]{2}-\d{2})\b")


def _mes(etiqueta: str) -> date:
    m = re.fullmatch(r"([A-Z][a-z]{2})-(\d{2})", etiqueta)
    return date(2000 + int(m.group(2)), MESES[m.group(1)], 1)


def _texto_pagina(ruta_pdf: str) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if TITULO_GASOLEO in t and TITULO_DIFERENCIAL in t:
                return t
    return ""


def _bloque(lineas: list[str], titulo: str) -> tuple[list[date], list[str]]:
    """(3 meses de la cabecera, lineas siguientes) del bloque que empieza en 'titulo'."""
    for i, linea in enumerate(lineas):
        if linea.strip().startswith(titulo):
            for j in range(i + 1, min(i + 4, len(lineas))):
                m = RE_CABECERA.match(lineas[j].strip())
                if m:
                    return [_mes(g) for g in m.groups()], lineas[j + 1 : j + 12]
    return [], []


def _valores(resto: str, patron: str) -> list[float | None]:
    """Los 5 valores de la fila (3 meses + M/M + Y/Y); '-' cuenta como hueco."""
    out: list[float | None] = []
    for tok in resto.split():
        if tok == "-":
            out.append(None)
        elif re.fullmatch(patron, tok):
            out.append(float(tok.rstrip("%")))
        if len(out) == 5:
            break
    return out + [None] * (5 - len(out))


def extraer_todos(ruta_pdf: str, issue_origen: str) -> list[CalefaccionFEM]:
    texto = _texto_pagina(ruta_pdf)
    if not texto:
        return []
    lineas = texto.split("\n")
    datos: dict[tuple[date, str], dict] = {}

    meses, filas = _bloque(lineas, TITULO_GASOLEO)
    for linea in filas:
        m = re.match(r"^(\w+), (?:EUR|€)/litre (.*)$", linea.strip())
        if m and m.group(1) in PAISES_GASOLEO:
            vals = _valores(m.group(2), r"-?\d+\.\d+")
            for mes, v in zip(meses, vals[:3], strict=True):
                datos.setdefault((mes, m.group(1)), {})["gasoleo_eur_l"] = v
            actual = datos[(meses[2], m.group(1))]
            actual["gasoleo_mm"], actual["gasoleo_yy"] = vals[3], vals[4]

    meses, filas = _bloque(lineas, TITULO_DIFERENCIAL)
    for linea in filas:
        m = re.match(r"^(\w+)\s+(.*)$", linea.strip())
        if m and m.group(1) in PAISES_DIFERENCIAL and ("%" in m.group(2) or "-" in m.group(2)):
            vals = _valores(m.group(2), r"-?\d+\.\d+%")
            for mes, v in zip(meses, vals[:3], strict=True):
                datos.setdefault((mes, m.group(1)), {})["diferencial_pct"] = v
            actual = datos[(meses[2], m.group(1))]
            actual["diferencial_mm"], actual["diferencial_yy"] = vals[3], vals[4]

    return [
        CalefaccionFEM(mes=mes, pais=pais, issue_origen=issue_origen, **vals)
        for (mes, pais), vals in sorted(datos.items())
        if any(v is not None for v in vals.values())
    ]
