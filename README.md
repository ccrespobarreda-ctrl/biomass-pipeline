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
│   └── argus\_spot.yaml
├── src/biomass\_pipeline/
│   ├── config.py               # constantes (4,72 MWh/t, 17 GJ/t) y rutas por entorno
│   ├── units.py                # conversiones de unidad centralizadas
│   ├── schemas/                # contratos de salida Pydantic (uno por tabla)
│   │   └── argus.py
│   ├── extractors/
│   │   ├── base.py             # utilidades comunes (pdfplumber + regex)
│   │   ├── argus\_spot.py       # PLANTILLA: extractor de la tabla spot
│   │   ├── registry.py         # registro dirigido por configuracion
│   │   └── llm.py              # extraccion con Claude, SOLO tablas enrevesadas
│   └── validation/
│       └── against\_sheet.py    # contraste contra el sheet historico
└── tests/
    └── test\_argus\_spot.py      # unitario (CI) + integracion (PDFs locales)
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
BIOMASS\_PDF\_DIR=./data/pdfs uv run pytest  # incluye integracion con PDFs reales
```

## Como anadir una tabla nueva

1. Crea el esquema en `schemas/` (el contrato: columnas y puertas de calidad).
2. Copia `extractors/argus\_spot.py` como plantilla y ajusta los patrones.
3. Registralo en `extractors/registry.py` y crea su `configs/<id>.yaml`.
4. Anade su test en `tests/` (fixture sintetico + integracion opcional).

Regla: **los PDFs y el sheet estan licenciados; NUNCA se commitean** (ya en `.gitignore`).

## Estado

* \[x] Fase 1 — esqueleto del repo
* \[x] Extractor de ejemplo: `argus\_spot` (validado 16/16 contra enero 2025)
* \[ ] Resto de tablas del Argus (asiaticos, fletes, premium Italia)
* \[ ] Tablas del FEM (biomass prices, ENDEX)
* \[ ] Transformacion (dbt) + carga PostgreSQL
* \[ ] Orquestacion (Dagster) + publicacion Zoho





\## Incidencias conocidas en los PDFs de origen



\*\*Issue de julio 2026 numerado como 148.\*\* El archivo se distribuyó con el

número 148 cuando por secuencia le corresponde el 184 (166 = enero 2025,

183 = junio 2026). Renombrarlo cambia el orden de consolidación: ver más abajo.



\*\*Junio 2026, fila Wood chips - Lithuania (Baltpool SM2).\*\* Los dos issues que

publican ese mes no coinciden:



\- issue 183 (junio 2026), columna Jun-26: 62.15 EUR/t / 22.91 EUR/MWh

\- issue 148 (julio 2026), columna Jun-26: 44.90 EUR/t / 16.55 EUR/MWh



El segundo valor coincide exactamente con lo que el issue 183 publica en su

columna Jun-25, lo que sugiere un arrastre de columna en el PDF de julio.

El resto de filas de esa misma columna sí coinciden entre ambos issues

(Germany 376.77, Austria 388.30, pellets Lithuania 246.24), por lo que no se

trata de un desalineamiento de indices en la extraccion. Se considera bueno

el dato del issue 183.

