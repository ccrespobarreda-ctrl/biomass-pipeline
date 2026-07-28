
  
    

  create  table "postgres"."analytics"."foto_semanal__dbt_tmp"
  
  
    as
  
  (
    -- Foto semanal: Argus (semanal) + FEM (mensual arrastrado) + columnas calculadas.
-- Esta tanda: calculos SIN tipo de cambio (€/t -> €/GJ -> €/MWh, y €/MWh -> €/GJ).
-- Los calculos con $->€ (asiaticos y CIF en euros, ENDEX en $) van en la siguiente
-- tanda, cuando extraigamos el tipo de cambio del FEM.

select
    a.fecha_issue,

    -- ===== ARGUS directo =====
    a.chips_cif_nwe_eur_gj,
    a.cif_nwe_usd_t,
    a.fob_baltics_eur_t,
    a.fob_baltics_eur_t / 17            as fob_baltics_eur_gj,
    a.fob_portugal_eur_t,
    a.fob_portugal_eur_t / 17           as fob_portugal_eur_gj,
    a.viet_japan_fit_usd_t,
    a.viet_korea_usd_t,
    a.gwangyang_usd_t,
    a.sumatra_fit_usd_t,
    a.malaysia_fit_usd_t,
    -- Italia premium (Mid): €/t directo, €/GJ y €/MWh calculados
    a.bulk_mid_eur_t,
    a.bulk_mid_eur_t / 17               as bulk_mid_eur_gj,
    a.bulk_mid_eur_t / 17 * 3.6         as bulk_mid_eur_mwh,
    a.bagged_mid_eur_t,
    a.bagged_mid_eur_t / 17             as bagged_mid_eur_gj,
    a.bagged_mid_eur_t / 17 * 3.6       as bagged_mid_eur_mwh,
    -- fletes (directos)
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

    -- ===== FEM directo + calculado =====
    -- residenciales: €/t directo, €/GJ y €/MWh calculados
    f.germany_depi_eur_t,
    f.germany_depi_eur_t / 17           as germany_depi_eur_gj,
    f.germany_depi_eur_t / 17 * 3.6     as germany_depi_eur_mwh,
    f.austria_propellet_eur_t,
    f.austria_propellet_eur_t / 17      as austria_propellet_eur_gj,
    f.austria_propellet_eur_t / 17 * 3.6 as austria_propellet_eur_mwh,
    f.swiss_preis_eur_t,
    f.swiss_preis_eur_t / 17            as swiss_preis_eur_gj,
    f.swiss_preis_eur_t / 17 * 3.6      as swiss_preis_eur_mwh,
    f.baltpool_eur_t,
    f.baltpool_eur_t / 17               as baltpool_eur_gj,
    f.baltpool_eur_t / 17 * 3.6         as baltpool_eur_mwh,
    -- ENDEX: por ahora solo la parte en euros (el €/t se extrae; $ va con FX despues)
    f.endex_ancla_eur_t,
    f.endex_ancla_eur_t / 17            as endex_ancla_eur_gj,
    f.endex_ancla_eur_t / 17 * 3.6      as endex_ancla_eur_mwh,
    -- series en €/MWh: €/GJ calculado dividiendo entre 3.6
    f.finland_eur_mwh,
    f.finland_eur_mwh / 3.6             as finland_eur_gj,
    f.sweden_eur_mwh,
    f.sweden_eur_mwh / 3.6              as sweden_eur_gj,
    f.lithuania_chips_eur_mwh,
    f.lithuania_chips_eur_mwh / 3.6     as lithuania_chips_eur_gj,
    -- pino US South (directos, en US$/s.ton)
    f.pine_pulpwood_usd,
    f.pine_chips_usd,
    f.pine_residuals_usd

from argus_semanal a
left join "postgres"."analytics"."fem_mensual_final" f
    on date_trunc('month', a.fecha_issue) = f.mes
order by a.fecha_issue
  );
  