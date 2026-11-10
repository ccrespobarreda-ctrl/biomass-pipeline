from biomass_pipeline.extractors import fem_biomass

RUTA = r"C:\Users\Cristina Crespo\Desktop\amor_y_datos\biomass-pipeline\biomass-pipeline\data\pdfs\entrada\FEM\FEM Issue 148 - July 2026.pdf"

for f in fem_biomass.extraer_todos(RUTA, "148"):
    print(f.mes, "baltpool:", f.baltpool_eur_t, "| chips MWh:", f.lithuania_chips_eur_mwh)