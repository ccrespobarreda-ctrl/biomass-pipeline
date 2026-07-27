"""Registro de extractores dirigido por configuracion."""

from . import (
    argus_asian,
    argus_freight,
    argus_italy,
    argus_pks,
    argus_spot,
    fem_biomass,
)

EXTRACTORES = {
    "argus_spot": argus_spot.extraer,
    "argus_asian": argus_asian.extraer,
    "argus_pks": argus_pks.extraer,
    "argus_italy": argus_italy.extraer,
    "argus_freight": argus_freight.extraer,
    "fem_biomass_prices": fem_biomass.extraer,
}


def obtener(id_tabla: str):
    if id_tabla not in EXTRACTORES:
        raise KeyError(f"no hay extractor registrado para '{id_tabla}'")
    return EXTRACTORES[id_tabla]
