"""Contratos de salida (Pydantic) para las tablas del Forest Energy Monitor (FEM)."""

from datetime import date

from pydantic import BaseModel, field_validator


class BiomassPricesFEM(BaseModel):
    """Fila de la tabla 'Biomass prices' para UN mes concreto de UN issue.

    Cada issue del FEM reporta varios meses; se emite una fila por mes (Opcion A:
    se guarda el rastro por issue, y meses vacios se rellenan desde issues posteriores).
    """

    mes: date
    issue_origen: str | None = None
    # tipo de cambio del mes (euros por 1 US$; la fila 'US dollar' del FEM vale 1.00)
    fx_eur_usd: float | None = None
    # residenciales (mensuales, fiables)
    germany_depi_eur_t: float | None = None       # col AI
    austria_propellet_eur_t: float | None = None  # col AL
    swiss_preis_eur_t: float | None = None        # col AF
    baltpool_eur_t: float | None = None           # col AO
    endex_ancla_eur_t: float | None = None        # col W (fila CIF ARA)
    # series trimestrales / best-effort
    finland_eur_mwh: float | None = None          # col H
    sweden_eur_mwh: float | None = None           # col F
    pine_pulpwood_usd: float | None = None        # col C
    pine_chips_usd: float | None = None           # col D
    pine_residuals_usd: float | None = None       # col E
    lithuania_chips_eur_mwh: float | None = None  # col J

    @field_validator("germany_depi_eur_t", "austria_propellet_eur_t", "swiss_preis_eur_t")
    @classmethod
    def rango_residencial(cls, v):
        if v is not None and not (150 <= v <= 600):
            raise ValueError(f"precio residencial fuera de rango plausible: {v}")
        return v

    @field_validator("fx_eur_usd")
    @classmethod
    def rango_fx(cls, v):
        if v is not None and not (0.5 <= v <= 1.5):
            raise ValueError(f"tipo de cambio fuera de rango plausible: {v}")
        return v