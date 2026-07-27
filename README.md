# biomass-pipeline

Pipeline de extraccion de datos de mercado de biomasa desde PDF (Argus Biomass
Markets, semanal + Forest Energy Monitor, mensual) hacia PostgreSQL y Zoho Analytics.

## Estructura

```
biomass-pipeline/
├── pyproject.toml              # dependencias (uv), ruff, pytest
├── Dockerfile                  # imagen reproducible
├── .github/workflows/ci.yml    # lint + tests en cada push
├── configs/                    # fichas de extraccion (una por tabla, declarativas)
│   └── argus_spot.yaml
├── src/biomass_pipeline/
│   ├── config.py               # constantes (4,72 MWh/t, 17 GJ/t) y rutas por entorno
│   ├── units.py                # conversiones de unidad centralizadas
│   ├── schemas/                # contratos de salida Pydantic (uno por tabla)
│   │   └── argus.py
│   ├── extractors/
│   │   ├── base.py             # utilidades comunes (pdfplumber + regex)
│   │   ├── argus_spot.py       # PLANTILLA: extractor de la tabla spot
│   │   ├── registry.py         # registro dirigido por configuracion
│   │   └── llm.py              # extraccion con Claude, SOLO tablas enrevesadas
│   └── validation/
│       └── against_sheet.py    # contraste contra el sheet historico
└── tests/
    └── test_argus_spot.py      # unitario (CI) + integracion (PDFs locales)
```

## Puesta en marcha (local)

```bash
# 1. instalar uv (si no lo tienes): https://docs.astral.sh/uv/
uv sync --extra dev            # crea el entorno e instala dependencias
cp .env.example .env           # y rellena las rutas a tus PDFs / sheet

# 2. activar los hooks de calidad
uv run pre-commit install

# 3. correr los tests
uv run pytest -m "not integration"        # rapidos (CI)
BIOMASS_PDF_DIR=./data/pdfs uv run pytest  # incluye integracion con PDFs reales
```

## Como anadir una tabla nueva

1. Crea el esquema en `schemas/` (el contrato: columnas y puertas de calidad).
2. Copia `extractors/argus_spot.py` como plantilla y ajusta los patrones.
3. Registralo en `extractors/registry.py` y crea su `configs/<id>.yaml`.
4. Anade su test en `tests/` (fixture sintetico + integracion opcional).

Regla: **los PDFs y el sheet estan licenciados; NUNCA se commitean** (ya en `.gitignore`).

## Estado

- [x] Fase 1 — esqueleto del repo
- [x] Extractor de ejemplo: `argus_spot` (validado 16/16 contra enero 2025)
- [ ] Resto de tablas del Argus (asiaticos, fletes, premium Italia)
- [ ] Tablas del FEM (biomass prices, ENDEX)
- [ ] Transformacion (dbt) + carga PostgreSQL
- [ ] Orquestacion (Dagster) + publicacion Zoho
