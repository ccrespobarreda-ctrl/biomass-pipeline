
  
    

  create  table "postgres"."analytics"."fem_mensual_final__dbt_tmp"
  
  
    as
  
  (
    -- Valor bueno de cada mes del FEM.
--
-- Datos FIRMES de mercado (fx_eur_usd, endex_ancla_eur_t): se toman del PROPIO issue
--     de ese mes (aquel cuyo "mes en curso" es ese mes), no del issue mas reciente que
--     lo mencione. Asi se evita coger versiones revisadas de meses posteriores
--     (p.ej. FX julio 0.85 no 0.86 ; ENDEX mayo 181.93 no 181.82).
-- Resto de columnas: el valor del issue mas reciente que las traiga rellenas (no nulas),
--     resuelto columna a columna (filosofia de rellenar huecos, ya validada vs Excel).

with base as (
    select
        mes,
        (array_agg(germany_depi_eur_t    order by issue_origen::int desc) filter (where germany_depi_eur_t is not null))[1]    as germany_depi_eur_t,
        (array_agg(austria_propellet_eur_t order by issue_origen::int desc) filter (where austria_propellet_eur_t is not null))[1] as austria_propellet_eur_t,
        (array_agg(swiss_preis_eur_t     order by issue_origen::int desc) filter (where swiss_preis_eur_t is not null))[1]     as swiss_preis_eur_t,
        (array_agg(baltpool_eur_t        order by issue_origen::int desc) filter (where baltpool_eur_t is not null))[1]        as baltpool_eur_t,
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

firmes as (
    -- datos firmes (FX y ENDEX): del propio issue cuyo mes-en-curso es ese mes
    select distinct on (f.mes)
        f.mes,
        f.fx_eur_usd,
        f.endex_ancla_eur_t
    from fem_mensual f
    join issue_actual ia
        on ia.issue_origen = f.issue_origen
       and ia.mes_actual = f.mes
    order by f.mes, f.issue_origen::int desc
)

select
    b.mes,
    fi.fx_eur_usd,
    b.germany_depi_eur_t,
    b.austria_propellet_eur_t,
    b.swiss_preis_eur_t,
    b.baltpool_eur_t,
    fi.endex_ancla_eur_t,
    b.finland_eur_mwh,
    b.sweden_eur_mwh,
    b.pine_pulpwood_usd,
    b.pine_chips_usd,
    b.pine_residuals_usd,
    b.lithuania_chips_eur_mwh
from base b
left join firmes fi on fi.mes = b.mes
order by b.mes
  );
  