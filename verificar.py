from biomass_pipeline.carga import conectar

SQL = """
select mes, issue_origen, lithuania_chips_eur_mwh
from fem_mensual
where mes >= '2026-06-01'
order by mes, issue_origen
"""

with conectar() as conn:
    with conn.cursor() as cur:
        cur.execute(SQL)
        for mes, issue, chips in cur.fetchall():
            print(mes, "| issue", issue, "| chips €/MWh:", chips)