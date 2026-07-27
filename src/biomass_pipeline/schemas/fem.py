"""Contratos de salida (Pydantic) para las tablas del Forest Energy Monitor (FEM).

El FEM es MENSUAL: su valor se arrastra en el sheet a las semanas del mes hasta
el issue siguiente.
"""

from datetime import date

from pydantic import BaseModel, field_validator


class BiomassPricesFEM(BaseModel):
    """Fila mensual de la tabla 'Biomass prices' (residenciales). Cols AF, AI, AL, AO."""

    mes: date
    germany_depi_eur_t: float | None  # col AI
    austria_propellet_eur_t: float | None  # col AL
    swiss_preis_eur_t: float | None  # col AF
    baltpool_eur_t: float | None  # col AO (a veces '-')
    finland_eur_mwh: float | None    # col H
    endex_ancla_eur_t: float | None    # col W (fila CIF ARA)

    @field_validator("germany_depi_eur_t", "austria_propellet_eur_t", "swiss_preis_eur_t")
    @classmethod
    def rango_residencial(cls, v):
        # los residenciales rondan 150-600 €/t; fuera de ahi es sospechoso
        if v is not None and not (150 <= v <= 600):
            raise ValueError(f"precio residencial fuera de rango plausible: {v}")
        return v
