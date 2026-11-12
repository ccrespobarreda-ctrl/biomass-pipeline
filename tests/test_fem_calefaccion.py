"""Tests del extractor de gasoleo / diferencial del FEM (P18).

Texto SINTETICO (numeros inventados) para que corra en CI sin PDFs licenciados.
"""

from datetime import date

from biomass_pipeline.extractors import fem_calefaccion

TEXTO_FALSO = """European Pellet Heating Economics
Heating oil prices
Oct-25 Sep-26 Oct-26 M/M Y/Y
Austria, €/litre 1.00 1.50 1.60 0.10 0.60
Germany, EUR/litre 0.90 1.40 1.70 0.30 0.80
Italy, EUR/litre 1.30 1.90 2.00 0.10 0.70
One Landscape Chart / Graph
Heating oil versus pellet price differential
Oct-25 Sep-26 Oct-26 M/M Y/Y
Austria 20.0% 40.0% 41.5% 1.5% 21.5%
France 22.0% - -
Germany -1.5% 30.0% 35.0% 5.0% 36.5%
Retail heating oil prices (including taxes) Differential between heating oil and pellet
"""


def test_parseo(monkeypatch):
    monkeypatch.setattr(fem_calefaccion, "_texto_pagina", lambda ruta: TEXTO_FALSO)
    filas = {(f.mes, f.pais): f for f in fem_calefaccion.extraer_todos("x.pdf", "999")}
    oct26, sep26, oct25 = date(2026, 10, 1), date(2026, 9, 1), date(2025, 10, 1)
    assert filas[(oct26, "Austria")].gasoleo_eur_l == 1.60
    assert filas[(oct26, "Austria")].diferencial_pct == 41.5
    assert filas[(oct25, "Germany")].diferencial_pct == -1.5
    assert filas[(sep26, "Italy")].gasoleo_eur_l == 1.90
    assert filas[(oct25, "France")].diferencial_pct == 22.0
    assert filas[(oct26, "Austria")].gasoleo_mm == 0.10
    assert filas[(oct26, "Germany")].diferencial_yy == 36.5
    assert filas[(sep26, "Austria")].gasoleo_mm is None  # M/M solo en el mes actual
    assert (oct26, "France") not in filas  # solo '-': no se emite fila vacia
    assert all(f.issue_origen == "999" for f in filas.values())


def test_sin_pagina(monkeypatch):
    monkeypatch.setattr(fem_calefaccion, "_texto_pagina", lambda ruta: "")
    assert fem_calefaccion.extraer_todos("x.pdf", "1") == []
