"""Contratos de salida (Pydantic) para las tablas del Argus Biomass Markets.

Un esquema por tabla. Las puertas de calidad (rangos plausibles, etc.) van aqui:
si un valor no encaja, la extraccion falla en voz alta en vez de escribir dato malo.
"""

from datetime import date

from pydantic import BaseModel, field_validator


class SpotPellets(BaseModel):
    """Bloque 'within 90 days (spot)'. Columnas L, M, P, R del mapeo."""

    fecha_issue: date
    cif_nwe_usd_t: float  # col M
    fob_baltics_eur_t: float  # col P
    fob_portugal_eur_t: float  # col R
    chips_cif_nwe_eur_gj: float  # col L

    @field_validator("cif_nwe_usd_t", "fob_baltics_eur_t", "fob_portugal_eur_t")
    @classmethod
    def rango_pellet_plausible(cls, v: float) -> float:
        if not (50 <= v <= 500):
            raise ValueError(f"precio de pellet fuera de rango plausible: {v}")
        return v

    @field_validator("chips_cif_nwe_eur_gj")
    @classmethod
    def rango_chips_plausible(cls, v: float) -> float:
        if not (3 <= v <= 30):
            raise ValueError(f"precio de chips fuera de rango plausible: {v}")
        return v
