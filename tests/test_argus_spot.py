"""Tests del extractor spot.

- test_parseo: usa un texto SINTETICO (numeros inventados). Verifica la logica de
  parseo sin depender de PDFs reales ni de datos licenciados -> corre en CI.
- test_integracion: corre contra PDFs reales locales; se SALTA si no estan
  (los PDFs del Argus estan licenciados y NO se commitean).
"""

import os
from datetime import date

import pytest

from biomass_pipeline.schemas.argus import SpotPellets

# Texto que imita el formato del Argus, con numeros inventados
TEXTO_FALSO = """
Wood pellets - within 90 days (spot)
cif NWE $/t 200.00 +0.50 201.0 202.0 203.0
fob Baltic €/t 180.00 -0.10 181.0 182.0 183.0
fob Portugal €/t 170.00 +1.00 171.0 172.0 173.0
NWE wood chips - within 90 days (spot) €/GJ
cif NWE 10.00 +0.20 10.1 10.2 10.3
"""


def test_parseo(monkeypatch):
    """El parser saca los 4 valores del texto y valida el esquema."""
    from biomass_pipeline.extractors import argus_spot

    monkeypatch.setattr(argus_spot, "texto_pdf", lambda ruta: TEXTO_FALSO)
    d = argus_spot.extraer("ignorado.pdf", date(2025, 1, 8))
    assert d.cif_nwe_usd_t == 200.0
    assert d.fob_baltics_eur_t == 180.0
    assert d.fob_portugal_eur_t == 170.0
    assert d.chips_cif_nwe_eur_gj == 10.0


def test_puerta_calidad():
    """Un precio absurdo debe hacer fallar la validacion."""
    with pytest.raises(ValueError):
        SpotPellets(
            fecha_issue=date(2025, 1, 8),
            cif_nwe_usd_t=9999,  # fuera de rango
            fob_baltics_eur_t=180,
            fob_portugal_eur_t=170,
            chips_cif_nwe_eur_gj=10,
        )


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("BIOMASS_PDF_DIR"),
    reason="define BIOMASS_PDF_DIR con PDFs reales para el test de integracion",
)
def test_integracion_enero_2025():
    """Contrasta la extraccion real contra valores conocidos del sheet."""
    from pathlib import Path

    from biomass_pipeline.extractors import argus_spot

    pdf = Path(os.environ["BIOMASS_PDF_DIR"]) / "20250108abm.pdf"
    d = argus_spot.extraer(str(pdf), date(2025, 1, 8))
    assert d.cif_nwe_usd_t == 192.07
    assert d.fob_baltics_eur_t == 170.10
    assert d.fob_portugal_eur_t == 167.50
    assert d.chips_cif_nwe_eur_gj == 9.30
