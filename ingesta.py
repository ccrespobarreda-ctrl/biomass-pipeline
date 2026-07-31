"""Ingesta automatica: carga los PDFs NUEVOS de las carpetas de entrada.

Mira dos subcarpetas de entrada (Argus y FEM), carga solo los PDFs que aun no
se han procesado (segun un registro en JSON), y anota los que carga bien para no
repetirlos. Reutiliza la logica de cargar_argus.py y cargar_fem.py.

Uso:
    uv run python ingesta.py

Deja los PDFs en:
    data/pdfs/entrada/Argus/   (nombres tipo 20250219abm.pdf)
    data/pdfs/entrada/FEM/     (nombres tipo 'FEM issue 170 - May 2025.pdf')
"""

import json
import re
from datetime import date
from pathlib import Path

from biomass_pipeline.carga import conectar, upsert
from biomass_pipeline.extractors import (
    argus_asian,
    argus_freight,
    argus_italy,
    argus_pks,
    argus_spot,
    fem_biomass,
)

# --- rutas (relativas a la carpeta del proyecto) ---
CARPETA_ARGUS = Path("data/pdfs/entrada/Argus")
CARPETA_FEM = Path("data/pdfs/entrada/FEM")
REGISTRO = Path("data/procesados.json")

EXTRACTORES_ARGUS = (argus_spot, argus_asian, argus_pks, argus_italy, argus_freight)


# ---------- registro de procesados ----------
def cargar_registro() -> dict[str, list[str]]:
    """Lee el registro; si no existe, empieza vacio."""
    if REGISTRO.exists():
        return json.loads(REGISTRO.read_text(encoding="utf-8"))
    return {"argus": [], "fem": []}


def guardar_registro(reg: dict[str, list[str]]) -> None:
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------- logica Argus (un PDF = una fila) ----------
def _fecha_argus(nombre: str) -> date:
    m = re.search(r"(\d{4})(\d{2})(\d{2})", nombre)
    if not m:
        raise ValueError(f"no encuentro fecha en el nombre: {nombre}")
    anio, mes, dia = map(int, m.groups())
    return date(anio, mes, dia)


def _cargar_argus(conn, pdf: Path) -> None:
    fecha = _fecha_argus(pdf.name)
    fila = {"fecha_issue": fecha}
    for ext in EXTRACTORES_ARGUS:
        datos = ext.extraer(str(pdf), fecha).model_dump()
        datos.pop("fecha_issue", None)
        fila.update(datos)
    upsert(conn, "argus_semanal", ["fecha_issue"], fila)


# ---------- logica FEM (un PDF = varias filas) ----------
def _issue_fem(nombre: str) -> str:
    m = re.search(r"issue\s+(\d+)", nombre, re.IGNORECASE)
    if not m:
        raise ValueError(f"no encuentro el numero de issue en el nombre: {nombre}")
    return m.group(1)


def _cargar_fem(conn, pdf: Path) -> None:
    issue = _issue_fem(pdf.name)
    for fila in fem_biomass.extraer_todos(str(pdf), issue):
        datos = fila.model_dump()
        datos["mes"] = datos["mes"].isoformat()
        upsert(conn, "fem_mensual", ["mes", "issue_origen"], datos)


# ---------- motor de ingesta ----------
def _procesar(conn, carpeta: Path, patron: str, ya_hechos: list[str], cargar_fn) -> int:
    """Carga los PDFs nuevos de 'carpeta'. Devuelve cuantos cargo bien."""
    if not carpeta.exists():
        print(f"  (aviso) no existe la carpeta {carpeta}, la salto")
        return 0
    nuevos = [p for p in sorted(carpeta.glob(patron)) if p.name not in ya_hechos]
    if not nuevos:
        print(f"  {carpeta.name}: nada nuevo")
        return 0
    ok = 0
    for pdf in nuevos:
        try:
            cargar_fn(conn, pdf)
            ya_hechos.append(pdf.name)   # solo se marca si NO hubo error
            ok += 1
            print(f"  {carpeta.name}: cargado {pdf.name}")
        except Exception as e:
            print(f"  {carpeta.name}: ERROR en {pdf.name}: {e}")
    return ok


def main() -> None:
    reg = cargar_registro()
    total = 0
    with conectar() as conn:
        total += _procesar(conn, CARPETA_ARGUS, "*abm*.pdf", reg["argus"], _cargar_argus)
        total += _procesar(conn, CARPETA_FEM, "*.pdf", reg["fem"], _cargar_fem)
    guardar_registro(reg)
    print(f"Ingesta terminada: {total} PDFs nuevos cargados.")


if __name__ == "__main__":
    main()