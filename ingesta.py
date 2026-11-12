"""Ingesta automatica: carga los PDFs NUEVOS de las carpetas de entrada.

Mira dos subcarpetas de entrada (Argus y FEM) y carga solo los PDFs que aun no estan:
  - ni en el registro local data/procesados.json,
  - ni en la base de datos (argus_semanal.fecha_issue / fem_mensual.issue_origen).
Lo segundo permite que funcione en GitHub Actions, donde el registro local no se guarda
entre ejecuciones.

Uso:
    uv run python ingesta.py

Deja los PDFs en:
    data/pdfs/entrada/Argus/   (cualquier PDF con la fecha AAAAMMDD en el nombre, p. ej.
                                20250219abm.pdf o 'Argus Biomass Markets 20260902_338289463.pdf')
    data/pdfs/entrada/FEM/     (nombres tipo 'FEM issue 170 - May 2025.pdf')

Sale con codigo 1 si algun PDF da error (asi GitHub Actions avisa por correo).
"""

import json
import re
import sys
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
    fem_calefaccion,
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


def claves_en_bd(conn) -> tuple[set[str], set[str]]:
    """Fechas Argus (aaaa-mm-dd) e issues FEM que ya estan en la base de datos."""
    with conn.cursor() as cur:
        cur.execute("select distinct fecha_issue from argus_semanal")
        fechas = {str(r[0])[:10] for r in cur.fetchall()}
        cur.execute("select distinct issue_origen from fem_mensual")
        issues = {str(r[0]) for r in cur.fetchall()}
    return fechas, issues


# ---------- logica Argus (un PDF = una fila) ----------
def _fecha_argus(nombre: str) -> date:
    """Primera fecha AAAAMMDD valida del nombre (20xx). Error si no hay ninguna."""
    for m in re.finditer(r"(20\d{2})(\d{2})(\d{2})", nombre):
        try:
            return date(*map(int, m.groups()))
        except ValueError:
            continue  # p. ej. un numero largo que no es una fecha
    raise ValueError(f"no encuentro fecha en el nombre: {nombre}")


def _es_pdf_argus(pdf: Path) -> bool:
    """Acepta cualquier PDF con fecha en el nombre (antes solo '*abm*.pdf')."""
    try:
        _fecha_argus(pdf.name)
        return True
    except ValueError:
        print(f"  Argus: (aviso) {pdf.name} no tiene fecha AAAAMMDD en el nombre, lo salto")
        return False


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


def _es_pdf_fem(pdf: Path) -> bool:
    try:
        _issue_fem(pdf.name)
        return True
    except ValueError:
        print(f"  FEM: (aviso) {pdf.name} no tiene 'issue NNN' en el nombre, lo salto")
        return False


def _cargar_fem(conn, pdf: Path) -> None:
    issue = _issue_fem(pdf.name)
    for fila in fem_biomass.extraer_todos(str(pdf), issue):
        datos = fila.model_dump()
        datos["mes"] = datos["mes"].isoformat()
        upsert(conn, "fem_mensual", ["mes", "issue_origen"], datos)
    cargar_calefaccion(conn, pdf, issue)


def cargar_calefaccion(conn, pdf: Path, issue: str) -> int:
    """Gasoleo de calefaccion y diferencial con el pellet (P18). Devuelve filas cargadas."""
    filas = fem_calefaccion.extraer_todos(str(pdf), issue)
    for fila in filas:
        datos = fila.model_dump()
        datos["mes"] = datos["mes"].isoformat()
        upsert(conn, "fem_calefaccion", ["mes", "pais", "issue_origen"], datos)
    return len(filas)


# ---------- motor de ingesta ----------
def _procesar(
    conn, carpeta: Path, ya_hechos: list[str], cargar_fn, filtro, ya_en_bd, orden=None
) -> tuple[int, int]:
    """Carga los PDFs nuevos de 'carpeta'. Devuelve (cargados, errores)."""
    if not carpeta.exists():
        print(f"  (aviso) no existe la carpeta {carpeta}, la salto")
        return 0, 0
    nuevos = [
        p
        for p in sorted(carpeta.glob("*.pdf"), key=orden)
        if p.name not in ya_hechos and filtro(p) and not ya_en_bd(p.name)
    ]
    if not nuevos:
        print(f"  {carpeta.name}: nada nuevo")
        return 0, 0
    ok = err = 0
    for pdf in nuevos:
        try:
            cargar_fn(conn, pdf)
            ya_hechos.append(pdf.name)  # solo se marca si NO hubo error
            ok += 1
            print(f"  {carpeta.name}: cargado {pdf.name}")
        except Exception as e:
            conn.rollback()
            err += 1
            print(f"  {carpeta.name}: ERROR en {pdf.name}: {e}")
    return ok, err


def main() -> None:
    reg = cargar_registro()
    total = errores = 0
    with conectar() as conn:
        fechas, issues = claves_en_bd(conn)
        ok, err = _procesar(
            conn,
            CARPETA_ARGUS,
            reg["argus"],
            _cargar_argus,
            _es_pdf_argus,
            ya_en_bd=lambda n: _fecha_argus(n).isoformat() in fechas,
        )
        total, errores = total + ok, errores + err
        ok, err = _procesar(
            conn,
            CARPETA_FEM,
            reg["fem"],
            _cargar_fem,
            _es_pdf_fem,
            ya_en_bd=lambda n: _issue_fem(n) in issues,
            orden=lambda p: int(_issue_fem(p.name)) if _es_pdf_fem_silencioso(p) else 0,
        )
        total, errores = total + ok, errores + err
    guardar_registro(reg)
    print(f"Ingesta terminada: {total} PDFs nuevos cargados, {errores} errores.")
    if errores:
        sys.exit(1)


def _es_pdf_fem_silencioso(pdf: Path) -> bool:
    return re.search(r"issue\s+(\d+)", pdf.name, re.IGNORECASE) is not None


if __name__ == "__main__":
    main()
