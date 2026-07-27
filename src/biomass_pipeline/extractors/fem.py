"""Contratos de salida (Pydantic) para las tablas del Forest Energy Monitor (FEM).

El FEM es MENSUAL: su valor se arrastra en el sheet a las semanas del mes hasta
el issue siguiente.
"""

from datetime import date

from pydantic import BaseModel, field_validator


class BiomassPricesFEM(BaseModel):
    """Fila mensual de la tabla 'Biomass prices'."""

    mes: date
    # --- residenciales (mensuales, fiables) ---
    germany_depi_eur_t: float | None       # col AI
    austria_propellet_eur_t: float | None  # col AL
    swiss_preis_eur_t: float | None        # col AF
    baltpool_eur_t: float | None           # col AO
    endex_ancla_eur_t: float | None        # col W (fila CIF ARA)
    # --- series trimestrales / best-effort (a menudo null en columnas mensuales) ---
    finland_eur_mwh: float | None          # col H
    sweden_eur_mwh: float | None           # col F
    pine_pulpwood_usd: float | None        # col C
    pine_chips_usd: float | None           # col D
    pine_residuals_usd: float | None       # col E
    lithuania_chips_eur_mwh: float | None  # col J

    @field_validator("germany_depi_eur_t", "austria_propellet_eur_t", "swiss_preis_eur_t")
    @classmethod
    def rango_residencial(cls, v):
        if v is not None and not (150 <= v <= 600):
            raise ValueError(f"precio residencial fuera de rango plausible: {v}")
        return v
