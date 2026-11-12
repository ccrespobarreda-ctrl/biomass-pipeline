"""Carga (o recarga) en Supabase la tabla fem_calefaccion desde PDFs del FEM ya bajados.

Sirve para el historico: ingesta.py solo procesa los issues NUEVOS, y los antiguos ya
estan en fem_mensual. Reprocesar no duplica (upsert por mes + pais + issue).

Uso:
    uv run python cargar_calefaccion.py                     # data/pdfs/entrada/FEM
    uv run python cargar_calefaccion.py "C:/ruta/a/los/PDFs"
"""

import sys
from pathlib import Path

from biomass_pipeline.carga import conectar
from ingesta import _es_pdf_fem, _issue_fem, cargar_calefaccion


def main() -> None:
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/pdfs/entrada/FEM")
    pdfs = [p for p in sorted(carpeta.rglob("*.pdf")) if _es_pdf_fem(p)]
    total = errores = 0
    with conectar() as conn:
        for pdf in pdfs:
            try:
                n = cargar_calefaccion(conn, pdf, _issue_fem(pdf.name))
                total += n
                print(f"  {pdf.name}: {n} filas")
            except Exception as e:
                conn.rollback()
                errores += 1
                print(f"  {pdf.name}: ERROR {e}")
    print(f"Calefaccion: {total} filas de {len(pdfs)} PDFs, {errores} errores.")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
