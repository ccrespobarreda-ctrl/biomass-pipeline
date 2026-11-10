"""Carga todos los PDFs del Argus de una carpeta a la tabla argus_semanal.

Uso:
    uv run python cargar_argus.py "C:\\ruta\\a\\tus\\pdfs"

Los PDFs del Argus deben llevar la fecha AAAAMMDD en el nombre, p.ej. 20250507abm.pdf
o 'Argus Biomass Markets 20260902_338289463.pdf'.
"""

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
)

EXTRACTORES = (argus_spot, argus_asian, argus_pks, argus_italy, argus_freight)


def fecha_de_nombre(nombre: str) -> date:
    for m in re.finditer(r"(20\d{2})(\d{2})(\d{2})", nombre):
        try:
            return date(*map(int, m.groups()))
        except ValueError:
            continue
    raise ValueError(f"no encuentro una fecha en el nombre del archivo: {nombre}")


def fila_argus(ruta_pdf: str, fecha: date) -> dict:
    """Ejecuta los 5 extractores del Argus y junta sus datos en una sola fila."""
    fila = {"fecha_issue": fecha}
    for ext in EXTRACTORES:
        datos = ext.extraer(ruta_pdf, fecha).model_dump()
        datos.pop("fecha_issue", None)
        fila.update(datos)
    return fila


def main(carpeta: str) -> None:
    pdfs = sorted(Path(carpeta).glob("*.pdf"))
    if not pdfs:
        print(f"No encontre PDFs del Argus en: {carpeta}")
        return
    ok = 0
    with conectar() as conn:
        for pdf in pdfs:
            try:
                fecha = fecha_de_nombre(pdf.name)
                fila = fila_argus(str(pdf), fecha)
                upsert(conn, "argus_semanal", ["fecha_issue"], fila)
                print(f"  cargado {fecha}  ({pdf.name})")
                ok += 1
            except Exception as e:  # un PDF con problema no debe parar el lote
                print(f"  ERROR en {pdf.name}: {e}")
    print(f"Listo: {ok}/{len(pdfs)} issues del Argus cargados en argus_semanal.")


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "./data/pdfs"
    main(carpeta)
