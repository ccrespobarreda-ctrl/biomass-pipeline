
  
    

  create  table "postgres"."analytics"."foto_semanal__dbt_tmp"
  
  
    as
  
  (
    -- Foto semanal: Argus (semanal) + FEM (mensual arrastrado) + columnas calculadas.
-- Calculos redondeados a 2 decimales. $<->€ con fx_eur_usd del FEM (euros por dolar):
--   $ -> €  = usd * fx    ;    € -> $  = eur / fx

select
    a.fecha_issue,
    f.mes as fecha_mes_fem,

    -- ===== ARGUS =====
    a.chips_cif_nwe_eur_gj,
    a.cif_nwe_usd_t,
    round(a.cif_nwe_usd_t * f.fx_eur_usd, 2)      as cif_nwe_eur_t,
    round(a.cif_nwe_usd_t * f.fx_eur_usd / 17, 2) as cif_nwe_eur_gj,
    a.fob_baltics_eur_t,
    round(a.fob_baltics_eur_t / 17, 2)            as fob_baltics_eur_gj,
    a.fob_portugal_eur_t,
    round(a.fob_portugal_eur_t / 17, 2)           as fob_portugal_eur_gj,
    a.viet_japan_fit_usd_t,
    round(a.viet_japan_fit_usd_t * f.fx_eur_usd, 2)             as viet_japan_fit_eur_t,
    round(a.viet_japan_fit_usd_t * f.fx_eur_usd / 17, 2)       as viet_japan_fit_eur_gj,
    round(a.viet_japan_fit_usd_t * f.fx_eur_usd / 17 * 3.6, 2) as viet_japan_fit_eur_mwh,
    a.viet_korea_usd_t,
    round(a.viet_korea_usd_t * f.fx_eur_usd, 2)             as viet_korea_eur_t,
    round(a.viet_korea_usd_t * f.fx_eur_usd / 17, 2)       as viet_korea_eur_gj,
    round(a.viet_korea_usd_t * f.fx_eur_usd / 17 * 3.6, 2) as viet_korea_eur_mwh,
    a.gwangyang_usd_t,
    round(a.gwangyang_usd_t * f.fx_eur_usd, 2)             as gwangyang_eur_t,
    round(a.gwangyang_usd_t * f.fx_eur_usd / 17, 2)       as gwangyang_eur_gj,
    round(a.gwangyang_usd_t * f.fx_eur_usd / 17 * 3.6, 2) as gwangyang_eur_mwh,
    a.sumatra_fit_usd_t,
    a.sumatra_usd_t,
    a.malaysia_fit_usd_t,
    a.malaysia_usd_t,
    a.bulk_mid_eur_t,
    round(a.bulk_mid_eur_t / 17, 2)               as bulk_mid_eur_gj,
    round(a.bulk_mid_eur_t / 17 * 3.6, 2)         as bulk_mid_eur_mwh,
    a.bagged_mid_eur_t,
    round(a.bagged_mid_eur_t / 17, 2)             as bagged_mid_eur_gj,
    round(a.bagged_mid_eur_t / 17 * 3.6, 2)       as bagged_mid_eur_mwh,
    a.aveiro_ara_eur_t,
    a.aveiro_cph_eur_t,
    a.aveiro_hull_eur_t,
    a.riga_ara_eur_t,
    a.riga_cph_eur_t,
    a.riga_stockholm_eur_t,
    a.mobile_ara_25kt_usd_t,
    a.mobile_ara_45kt_usd_t,
    a.savannah_ara_25kt_usd_t,
    a.savannah_ara_45kt_usd_t,
    a.vancouver_ara_45kt_usd_t,

    -- ===== FEM =====
    f.germany_depi_eur_t,
    round(f.germany_depi_eur_t / 17, 2)           as germany_depi_eur_gj,
    round(f.germany_depi_eur_t / 17 * 3.6, 2)     as germany_depi_eur_mwh,
    f.austria_propellet_eur_t,
    round(f.austria_propellet_eur_t / 17, 2)      as austria_propellet_eur_gj,
    round(f.austria_propellet_eur_t / 17 * 3.6, 2) as austria_propellet_eur_mwh,
    f.swiss_preis_eur_t,
    round(f.swiss_preis_eur_t / 17, 2)            as swiss_preis_eur_gj,
    round(f.swiss_preis_eur_t / 17 * 3.6, 2)      as swiss_preis_eur_mwh,
    f.baltpool_eur_t,
    round(f.baltpool_eur_t / 17, 2)               as baltpool_eur_gj,
    round(f.baltpool_eur_t / 17 * 3.6, 2)         as baltpool_eur_mwh,
    f.endex_ancla_eur_t,
    round(f.endex_ancla_eur_t / 17, 2)            as endex_ancla_eur_gj,
    round(f.endex_ancla_eur_t / 17 * 3.6, 2)      as endex_ancla_eur_mwh,
    round(f.endex_ancla_eur_t / f.fx_eur_usd, 2)             as endex_ancla_usd_t,
    round(f.endex_ancla_eur_t / f.fx_eur_usd / 17, 2)       as endex_ancla_usd_gj,
    round(f.endex_ancla_eur_t / f.fx_eur_usd / 17 * 3.6, 2) as endex_ancla_usd_mwh,
    f.finland_eur_mwh,
    round(f.finland_eur_mwh / 3.6, 2)             as finland_eur_gj,
    f.sweden_eur_mwh,
    round(f.sweden_eur_mwh / 3.6, 2)              as sweden_eur_gj,
    f.lithuania_chips_eur_mwh,
    round(f.lithuania_chips_eur_mwh / 3.6, 2)     as lithuania_chips_eur_gj,
    f.pine_pulpwood_usd,
    f.pine_chips_usd,
    f.pine_residuals_usd

from argus_semanal a
left join "postgres"."analytics"."fem_mensual_final" f
    on date_trunc('month', a.fecha_issue) = f.mes
order by a.fecha_issue
  );
  