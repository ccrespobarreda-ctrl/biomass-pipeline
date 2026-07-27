"""Conversiones de unidad. Centralizadas para que la logica viva en un solo sitio."""

from .config import GJ_POR_MWH, GJ_POR_TONELADA, MWH_POR_TONELADA


def eur_t_a_gj(valor_t: float) -> float:
    return valor_t / GJ_POR_TONELADA


def eur_t_a_mwh(valor_t: float) -> float:
    return valor_t / MWH_POR_TONELADA


def gj_a_mwh(valor_gj: float) -> float:
    return valor_gj * GJ_POR_MWH


def usd_a_eur(valor_usd: float, fx_eur_por_usd: float) -> float:
    """Convierte USD a EUR con el tipo de cambio del mes (tabla FX del FEM)."""
    return valor_usd * fx_eur_por_usd
