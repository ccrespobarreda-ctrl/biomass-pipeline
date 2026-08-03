"""Extractor de la tabla 'Biomass prices' del FEM.

extraer_todos() emite UNA fila por mes. Al cargarlas en orden, los meses que un issue
trae vacios se rellenan desde issues posteriores.

SERIES TRIMESTRALES (pinos y Suecia): el FEM no las publica en las columnas mensuales
(siempre '-'); solo en las trimestrales (1Q24, 1Q25...). Criterio elegido: el valor de
la ultima columna trimestral se asigna a los TRES meses de ese trimestre (1Q25 ->
enero, febrero y marzo de 2025). Como los issues posteriores revisan el trimestre,
fem_mensual_final se queda con la revision mas reciente.

LIMITACION CONOCIDA: en el PDF algunos valores llevan un subindice (p.ej. "33.16 Q4")
que indica que el dato es de otro trimestre distinto al de la cabecera. Ese subindice
NO sobrevive a la extraccion de texto, asi que no se puede detectar: en esos casos el
valor puede quedar fechado un trimestre despues de lo que le corresponde.
"""

import re
from datetime import date

import pdfplumber

from ..schemas.fem import BiomassPricesFEM

PAGINA_TABLA = 2
MARCADOR_CAMBIO = "Exchange rates against the US dollar"
UNIDAD_PINO = "US$/s.ton"
ETIQUETA_SUECIA = "Energy wood/ biomass - Sweden"
MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# Filas mensuales: se exigen decimales a proposito, porque en algunas filas hay rangos
# ("185-200") que con enteros se partirian en dos valores falsos.
RE_NUM = r"-?\d+\.\d+|(?<= )-(?= )"
# Filas trimestrales: aqui SI hay enteros ("32", "381"). Si no se aceptaran, el regex
# los saltaria y desplazaria todas las columnas siguientes (bug silencioso).
RE_NUM_ENTEROS = r"-?\d+(?:\.\d+)?|(?<= )-(?= )"

# series que solo se publican por trimestres: campo del esquema -> (etiqueta, unidad)
SERIES_TRIMESTRALES = {
    "sweden_eur_mwh": (ETIQUETA_SUECIA, "€/MWh"),
    "pine_pulpwood_usd": ("Pine pulpwood", UNIDAD_PINO),
    "pine_chips_usd": ("In-wood pine chips", UNIDAD_PINO),
    "pine_residuals_usd": ("Pine process residuals", UNIDAD_PINO),
}


def _texto_pagina(ruta_pdf: str, pag: int = PAGINA_TABLA) -> str:
    with pdfplumber.open(ruta_pdf) as pdf:
        return pdf.pages[pag].extract_text() or ""


def _texto_pagina_por_marcador(ruta_pdf: str, marcador: str) -> str:
    """La pagina del cambio se MUEVE entre issues (16, 17 o 18): se busca por contenido."""
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if marcador in t:
                return t
    return ""


def _fx_por_mes(ruta_pdf: str) -> dict[date, float]:
    """{primer dia del mes: euros por 1 USD} de la fila 'Euro' de la tabla de cambio."""
    texto = _texto_pagina_por_marcador(ruta_pdf, MARCADOR_CAMBIO)
    cab = re.search(
        r"(?m)^[ \t]*([A-Z][a-z]{2}-\d{2}) +([A-Z][a-z]{2}-\d{2}) +([A-Z][a-z]{2}-\d{2}) +M/M",
        texto,
    )
    fila = re.search(r"(?m)^[ \t]*Euro +(\d+\.\d+) +(\d+\.\d+) +(\d+\.\d+)\b", texto)
    if not cab or not fila:
        return {}
    return {_mes_a_fecha(cab.group(i)): float(fila.group(i)) for i in (1, 2, 3)}


def _columnas(texto: str) -> list[str]:
    """Etiquetas de periodo de la cabecera (trimestrales + mensuales)."""
    for line in texto.split("\n"):
        if "chg on" in line:
            return re.findall(r"[0-9]Q\d{2}|[A-Z][a-z]{2}-\d{2}", line)
    return []


def _ultimo_trimestre(cols: list[str]) -> tuple[int | None, str]:
    """(posicion, etiqueta) de la ultima columna TRIMESTRAL. P.ej. (1, '1Q25')."""
    idxs = [i for i, c in enumerate(cols) if re.fullmatch(r"\dQ\d{2}", c)]
    return (idxs[-1], cols[idxs[-1]]) if idxs else (None, "")


def _meses_del_trimestre(etiqueta: str) -> list[date]:
    """'1Q25' -> [1-ene-2025, 1-feb-2025, 1-mar-2025]."""
    m = re.fullmatch(r"(\d)Q(\d{2})", etiqueta)
    if not m:
        return []
    trimestre, anio = int(m.group(1)), 2000 + int(m.group(2))
    primero = (trimestre - 1) * 3 + 1
    return [date(anio, primero + k, 1) for k in range(3)]


def _nums_fila(texto: str, etiqueta: str, unidad: str, patron: str = RE_NUM) -> list[str] | None:
    lineas = texto.split("\n")
    for i, line in enumerate(lineas):
        if etiqueta in line:
            for j in range(i, min(i + 3, len(lineas))):
                if unidad in lineas[j]:
                    return re.findall(patron, lineas[j].split(unidad, 1)[1])
    return None


def _valor(texto: str, etiqueta: str, unidad: str, idx: int) -> float | None:
    nums = _nums_fila(texto, etiqueta, unidad)
    if nums and len(nums) > idx and nums[idx] != "-":
        return float(nums[idx])
    return None


def _valor_ent(texto: str, etiqueta: str, unidad: str, idx: int | None) -> float | None:
    """Como _valor pero tolerante a enteros (para las filas trimestrales)."""
    if idx is None:
        return None
    nums = _nums_fila(texto, etiqueta, unidad, RE_NUM_ENTEROS)
    if nums and len(nums) > idx and nums[idx] != "-":
        return float(nums[idx])
    return None


def _mes_a_fecha(etiqueta: str) -> date:
    m = re.match(r"([A-Z][a-z]{2})-(\d{2})", etiqueta)
    return date(2000 + int(m.group(2)), MESES[m.group(1)], 1)


def extraer_todos(ruta_pdf: str, issue_origen: str) -> list[BiomassPricesFEM]:
    """Filas del issue: sus meses mensuales + los 3 meses de su ultimo trimestre.

    Los meses que aparecen en ambos sitios se FUSIONAN en una sola fila (la clave de
    fem_mensual es mes+issue: dos filas del mismo mes e issue se pisarian).
    """
    texto = _texto_pagina(ruta_pdf)
    cols = _columnas(texto)
    fx_map = _fx_por_mes(ruta_pdf)
    datos: dict[date, dict] = {}

    # --- columnas MENSUALES ---
    for idx, etiqueta in enumerate(cols):
        if not re.match(r"[A-Z][a-z]{2}-\d{2}", etiqueta):
            continue  # las trimestrales se tratan aparte, mas abajo
        f_mes = _mes_a_fecha(etiqueta)
        fila = {
            "mes": f_mes,
            "issue_origen": issue_origen,
            "fx_eur_usd": fx_map.get(f_mes),
            "germany_depi_eur_t": _valor(
                texto, "Heating wood pellets - Germany", "€/tonne", idx
            ),
            "austria_propellet_eur_t": _valor(
                texto, "Heating wood pellets - Austria", "€/tonne", idx
            ),
            "swiss_preis_eur_t": _valor(
                texto, "Heating wood pellets - Switzerland", "€/tonne", idx
            ),
            "baltpool_eur_t": _valor(texto, "Heating wood pellets - Lithuania", "€/tonne", idx),
            "endex_ancla_eur_t": _valor(texto, "Industrial wood pellets", "€/tonne", idx),
            "finland_eur_mwh": _valor(texto, "Forest biomass - Finland", "€/MWh", idx),
            "lithuania_chips_eur_mwh": _valor(texto, "Wood chips - Lith", "€/MWh", idx),
        }
        # si el FEM llegase a publicar estas series por meses, se usa el valor mensual
        for campo, (etq, uni) in SERIES_TRIMESTRALES.items():
            fila[campo] = _valor_ent(texto, etq, uni, idx)
        datos[f_mes] = fila

    # --- columna TRIMESTRAL: su valor va a los 3 meses del trimestre ---
    idx_trim, etiqueta_trim = _ultimo_trimestre(cols)
    if idx_trim is not None:
        trimestrales = {
            campo: _valor_ent(texto, etq, uni, idx_trim)
            for campo, (etq, uni) in SERIES_TRIMESTRALES.items()
        }
        for f_mes in _meses_del_trimestre(etiqueta_trim):
            fila = datos.setdefault(
                f_mes,
                {"mes": f_mes, "issue_origen": issue_origen, "fx_eur_usd": fx_map.get(f_mes)},
            )
            for campo, valor in trimestrales.items():
                if valor is not None and fila.get(campo) is None:
                    fila[campo] = valor

    return [BiomassPricesFEM(**datos[m]) for m in sorted(datos)]


def extraer(ruta_pdf: str, mes=None, issue_origen: str = "") -> BiomassPricesFEM | None:
    """Compatibilidad: devuelve solo el mes mas reciente del issue.

    Para la carga real usa extraer_todos(), que emite todos los meses.
    """
    filas = extraer_todos(ruta_pdf, issue_origen)
    return filas[-1] if filas else None