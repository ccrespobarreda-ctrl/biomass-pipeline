-- Valor bueno de cada mes del FEM.
--
-- FX: se toma del PROPIO issue de ese mes (aquel cuyo "mes en curso" es ese mes),
--     no del issue mas reciente que lo mencione. Asi se evita coger versiones
--     revisadas de meses posteriores (p.ej. julio: 0.85 de su issue, no 0.86 revisado).
-- Resto de columnas: el valor del issue mas reciente que las traiga rellenas (no nulas),
--     resuelto columna a columna (filosofia de rellenar huecos, ya validada).

with base as (
    select
        mes,
        (array_agg(germany_depi_eur_t    order by issue_origen::int desc) filter (where germany_depi_eur_t is not null))[1]    as germany_depi_eur_t,
        (array_agg(austria_propellet_eur_t order by issue_origen::int desc) filter (where austria_propellet_eur_t is not null))[1] as austria_propellet_eur_t,
        (array_agg(swiss_preis_eur_t     order by issue_origen::int desc) filter (where swiss_preis_eur_t is not null))[1]     as swiss_preis_eur_t,
        (array_agg(baltpool_eur_t        order by issue_origen::int desc) filter (where baltpool_eur_t is not null))[1]        as baltpool_eur_t,
        (array_agg(endex_ancla_eur_t     order by issue_origen::int desc) filter (where endex_ancla_eur_t is not null))[1]     as endex_ancla_eur_t,
        (array_agg(finland_eur_mwh       order by issue_origen::int desc) filter (where finland_eur_mwh is not null))[1]       as finland_eur_mwh,
        (array_agg(sweden_eur_mwh        order by issue_origen::int desc) filter (where sweden_eur_mwh is not null))[1]        as sweden_eur_mwh,
        (array_agg(pine_pulpwood_usd     order by issue_origen::int desc) filter (where pine_pulpwood_usd is not null))[1]     as pine_pulpwood_usd,
        (array_agg(pine_chips_usd        order by issue_origen::int desc) filter (where pine_chips_usd is not null))[1]        as pine_chips_usd,
        (array_agg(pine_residuals_usd    order by issue_origen::int desc) filter (where pine_residuals_usd is not null))[1]    as pine_residuals_usd,
        (array_agg(lithuania_chips_eur_mwh order by issue_origen::int desc) filter (where lithuania_chips_eur_mwh is not null))[1] as lithuania_chips_eur_mwh
    from fem_mensual
    group by mes
),

issue_actual as (
    select issue_origen, max(mes) as mes_actual
    from fem_mensual
    group by issue_origen
),

fx as (
    select distinct on (f.mes)
        f.mes,
        f.fx_eur_usd
    from fem_mensual f
    join issue_actual ia
        on ia.issue_origen = f.issue_origen
       and ia.mes_actual = f.mes
    order by f.mes, f.issue_origen::int desc
)

select
    b.mes,
    fx.fx_eur_usd,
    b.germany_depi_eur_t,
    b.austria_propellet_eur_t,
    b.swiss_preis_eur_t,
    b.baltpool_eur_t,
    b.endex_ancla_eur_t,
    b.finland_eur_mwh,
    b.sweden_eur_mwh,
    b.pine_pulpwood_usd,
    b.pine_chips_usd,
    b.pine_residuals_usd,
    b.lithuania_chips_eur_mwh
from base b
left join fx on fx.mes = b.mes
order by b.mes