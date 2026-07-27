"""Registro de extractores dirigido por configuracion.

Cada tabla se declara en configs/*.yaml (la 'ficha de extraccion') y se asocia
aqui a su funcion de extraccion. Anadir una tabla nueva = anadir un yaml + una
funcion + una linea en este mapa. El motor del pipeline no cambia.
"""
from . import argus_spot, fem_biomass

# id de tabla -> funcion extractora
EXTRACTORES = {
    "argus_spot": argus_spot.extraer,
    "fem_biomass_prices": fem_biomass.extraer,
    # "argus_asian": argus_asian.extraer,     # <- proxima tabla
    # "argus_freight": argus_freight.extraer,
}


def obtener(id_tabla: str):
    if id_tabla not in EXTRACTORES:
        raise KeyError(f"no hay extractor registrado para '{id_tabla}'")
    return EXTRACTORES[id_tabla]
