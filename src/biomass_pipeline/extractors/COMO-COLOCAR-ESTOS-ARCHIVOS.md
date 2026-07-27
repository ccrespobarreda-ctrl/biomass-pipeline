# Cómo colocar estos extractores en el repo

## Archivos que REEMPLAZAN a los que ya tienes
(sobrescribe los existentes con estos)

| Archivo | Va en | Qué cambia |
|---|---|---|
| `fem.py` | `src/biomass_pipeline/schemas/fem.py` | añade Suecia, pino x3, chips Lituania |
| `fem_biomass.py` | `src/biomass_pipeline/extractors/fem_biomass.py` | extrae esas filas nuevas |
| `argus.py` | `src/biomass_pipeline/schemas/argus.py` | añade 4 esquemas: Asian, PKS, Italy, Freight |
| `registry.py` | `src/biomass_pipeline/extractors/registry.py` | registra los 4 extractores nuevos |

## Archivos NUEVOS
(no existían; añádelos)

| Archivo | Va en |
|---|---|
| `argus_asian.py` | `src/biomass_pipeline/extractors/argus_asian.py` |
| `argus_pks.py` | `src/biomass_pipeline/extractors/argus_pks.py` |
| `argus_italy.py` | `src/biomass_pipeline/extractors/argus_italy.py` |
| `argus_freight.py` | `src/biomass_pipeline/extractors/argus_freight.py` |

## Después de colocarlos

```
uv run ruff check .
uv run pytest -m "not integration"
git add .
git commit -m "Anadir extractores Argus (asiaticos, PKS, Italia, fletes) y ampliar FEM"
git push
```

## Notas importantes

- **Verificado**: todos extraen bien contra los PDFs de 2025 (asiáticos, PKS, Italia,
  los 11 fletes, y el FEM completo). ruff en verde.
- **Best-effort (no validables contra el sheet)**: asiáticos, PKS, Italia y fletes NO
  están poblados en tu histórico, así que se verifican ojeando el PDF, no automáticamente.
- **Series trimestrales**: pino, Suecia, Finlandia y chips de Lituania salen null la
  mayoría de meses (el dato en origen es trimestral). Es la decisión que tomaste. Si
  algún día quieres rellenarlas con el último valor disponible, en `fem_biomass.py` está
  la función `_valor_ultimo` lista para usar en esas filas.
- **Fletes**: recuerda que Aveiro y Riga vienen en €/t y Mobile/Savannah/Vancouver en $/t.
