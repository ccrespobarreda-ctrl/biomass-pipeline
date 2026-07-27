"""Contratos de salida (Pydantic) para las tablas del Argus Biomass Markets.

Un esquema por tabla. Las puertas de calidad (rangos plausibles) van aqui.
Nota: asiaticos, fletes, PKS y premium Italia NO estan poblados en el sheet
historico, asi que se validan ojeando el PDF, no automaticamente.
"""

from datetime import date

from pydantic import BaseModel, field_validator


class SpotPellets(BaseModel):
    """Bloque 'within 90 days (spot)'. Columnas L, M, P, R del mapeo."""

    fecha_issue: date
    cif_nwe_usd_t: float          # col M
    fob_baltics_eur_t: float      # col P
    fob_portugal_eur_t: float     # col R
    chips_cif_nwe_eur_gj: float   # col L

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


class AsianPellets(BaseModel):
    """Tabla 'Asian industrial wood pellets'. Columnas AR, AV, AZ."""

    fecha_issue: date
    viet_japan_fit_usd_t: float | None   # col AR
    viet_korea_usd_t: float | None       # col AV
    gwangyang_usd_t: float | None        # col AZ


class PalmKernelShells(BaseModel):
    """Tabla 'Asian palm kernel shells' (variante to Japan FIT). Columnas BO, BQ."""

    fecha_issue: date
    sumatra_fit_usd_t: float | None      # col BO
    malaysia_fit_usd_t: float | None     # col BQ


class ItalyPremium(BaseModel):
    """Tabla 'European premium wood pellets' (Italia, valor Mid). Columnas Z, AC."""

    fecha_issue: date
    bulk_mid_eur_t: float | None         # col Z
    bagged_mid_eur_t: float | None       # col AC


class Freight(BaseModel):
    """Tabla 'Wood pellet freight indications'. Columnas BD-BN.

    OJO unidades: Aveiro y Riga en €/t; Mobile/Savannah/Vancouver en $/t.
    """

    fecha_issue: date
    aveiro_ara_eur_t: float | None        # BD
    aveiro_cph_eur_t: float | None        # BE
    aveiro_hull_eur_t: float | None       # BF
    riga_ara_eur_t: float | None          # BG
    riga_cph_eur_t: float | None          # BH
    riga_stockholm_eur_t: float | None    # BI
    mobile_ara_25kt_usd_t: float | None   # BJ
    mobile_ara_45kt_usd_t: float | None   # BK
    savannah_ara_25kt_usd_t: float | None # BL
    savannah_ara_45kt_usd_t: float | None # BM
    vancouver_ara_45kt_usd_t: float | None  # BN
