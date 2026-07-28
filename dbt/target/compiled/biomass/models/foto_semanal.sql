-- Foto semanal: una fila por miercoles del Argus, con el dato del FEM del mes
-- correspondiente "arrastrado". Esta version trae todas las columnas DIRECTAS
-- (las que se extraen tal cual). Los calculos (€/GJ, €/MWh, $->€) van en la
-- siguiente tanda, encima de estas.

select
    a.fecha_issue,

    -- ===== ARGUS (semanal) =====
    -- spot
    a.chips_cif_nwe_eur_gj,
    a.cif_nwe_usd_t,
    a.fob_baltics_eur_t,
    a.fob_portugal_eur_t,
    -- asiaticos
    a.viet_japan_fit_usd_t,
    a.viet_korea_usd_t,
    a.gwangyang_usd_t,
    -- PKS
    a.sumatra_fit_usd_t,
    a.malaysia_fit_usd_t,
    -- premium Italia (Mid)
    a.bulk_mid_eur_t,
    a.bagged_mid_eur_t,
    -- fletes
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

    -- ===== FEM (mensual, arrastrado) =====
    f.germany_depi_eur_t,
    f.austria_propellet_eur_t,
    f.swiss_preis_eur_t,
    f.baltpool_eur_t,
    f.endex_ancla_eur_t,
    f.finland_eur_mwh,
    f.sweden_eur_mwh,
    f.pine_pulpwood_usd,
    f.pine_chips_usd,
    f.pine_residuals_usd,
    f.lithuania_chips_eur_mwh

from argus_semanal a
left join "postgres"."analytics"."fem_mensual_final" f
    on date_trunc('month', a.fecha_issue) = f.mes
order by a.fecha_issue