-- Test singular: en foto_semanal, €/MWh debe ser €/GJ * 3.6 (misma base energetica).
-- dbt: el test PASA si esta consulta NO devuelve filas (ninguna fila incumple la regla).
-- Se deja un margen de 0.05 por el redondeo a 2 decimales de cada columna por separado.

with comprobaciones as (
    select fecha_issue, 'germany_depi'  as serie, germany_depi_eur_gj  as eur_gj, germany_depi_eur_mwh  as eur_mwh from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'austria_propellet', austria_propellet_eur_gj, austria_propellet_eur_mwh from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'swiss_preis',   swiss_preis_eur_gj,   swiss_preis_eur_mwh   from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'baltpool',      baltpool_eur_gj,      baltpool_eur_mwh      from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'endex_ancla',   endex_ancla_eur_gj,   endex_ancla_eur_mwh   from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'bulk_mid',      bulk_mid_eur_gj,      bulk_mid_eur_mwh      from {{ ref('foto_semanal') }}
    union all
    select fecha_issue, 'bagged_mid',    bagged_mid_eur_gj,    bagged_mid_eur_mwh    from {{ ref('foto_semanal') }}
)

select *
from comprobaciones
where eur_gj is not null
  and eur_mwh is not null
  and abs(eur_mwh - eur_gj * 3.6) > 0.05