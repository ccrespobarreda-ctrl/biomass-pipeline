"""Carga los PDFs del FEM a la tabla fem_mensual (con relleno desde issues posteriores).

Uso:
    uv run python cargar_fem.py "C:\\ruta\\a\\tus\\pdfs\\FEM"

Cada PDF del FEM debe llevar su numero de issue en el nombre, p.ej.
'FEM issue 170 - May 2025.pdf'. Se cargan en orden de issue para que el relleno
ocurra bien.
"""

import re
import sys
from pathlib import Path

from biomass_pipeline.carga import conectar, upsert
from biomass_pipeline.extractors import fem_biomass


def issue_de_nombre(nombre: str) -> str:
    m = re.search(r"issue\s+(\d+)", nombre, re.IGNORECASE)
    if not m:
        raise ValueError(f"no encuentro el numero de issue en el nombre: {nombre}")
    return m.group(1)


def main(carpeta: str) -> None:
    pdfs = sorted(Path(carpeta).glob("*.pdf"), key=lambda p: int(issue_de_nombre(p.name)))
    if not pdfs:
        print(f"No encontre PDFs del FEM en: {carpeta}")
        return
    total = ok = 0
    with conectar() as conn:
        for pdf in pdfs:
            try:
                issue = issue_de_nombre(pdf.name)
                filas = fem_biomass.extraer_todos(str(pdf), issue)
                for fila in filas:
                    datos = fila.model_dump()
                    datos["mes"] = datos["mes"].isoformat()
                    upsert(conn, "fem_mensual", ["mes", "issue_origen"], datos)
                    total += 1
                print(f"  issue {issue}: {len(filas)} meses cargados ({pdf.name})")
                ok += 1
            except Exception as e:
                print(f"  ERROR en {pdf.name}: {e}")
    print(f"Listo: {ok}/{len(pdfs)} issues del FEM, {total} filas mes-issue en fem_mensual.")


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "./data/pdfs/FEM"
    main(carpeta)
