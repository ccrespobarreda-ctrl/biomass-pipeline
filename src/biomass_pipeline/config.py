"""Constantes de negocio y ajustes por entorno.

Las rutas y credenciales se leen de variables de entorno (nunca hardcodeadas
ni commiteadas). En local se cargan desde un .env; en produccion, desde el
gestor de secretos (Zoho Vault).
"""

import os
from pathlib import Path

# --- constantes de conversion (las dan las propias fuentes) ---
MWH_POR_TONELADA = 4.72  # 1 t de pellet = 4,72 MWh
GJ_POR_TONELADA = 17.0  # 1 t de pellet = 17 GJ
GJ_POR_MWH = 3.6  # 1 MWh = 3,6 GJ

# --- rutas (configurables por entorno) ---
# Carpeta con los PDFs de entrada. Cambia esto en tu .env local.
PDF_DIR = Path(os.getenv("BIOMASS_PDF_DIR", "./data/pdfs"))
# Sheet historico para validar extracciones contra el dato conocido.
SHEET_HISTORICO = Path(os.getenv("BIOMASS_SHEET_HISTORICO", "./data/historico.xlsx"))
SHEET_HOJA = os.getenv("BIOMASS_SHEET_HOJA", "B2E1")
