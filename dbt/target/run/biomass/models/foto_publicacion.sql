
  
    

  create  table "postgres"."analytics"."foto_publicacion__dbt_tmp"
  
  
    as
  
  (
    -- Capa de PRESENTACION para Zoho: los mismos datos que foto_semanal, pero con los
-- nombres y el orden EXACTOS del sheet (columnas A a BR = 70 columnas).
--
-- Por que un modelo aparte y no renombrar foto_semanal:
--   * foto_semanal conserva nombres tecnicos (snake_case), asi el SQL y los tests
--     siguen siendo simples (los nombres con espacios/€/$ exigirian comillas dobles).
--   * el test tests/coherencia_unidades.sql usa los nombres tecnicos: si se
--     renombrara foto_semanal, ese test dejaria de funcionar.
--
-- FLETES: Aveiro y Riga vienen en €/t en el PDF de Argus y se publican convertidos a
-- $/t (columnas aveiro_*_usd_t, riga_*_usd_t de foto_semanal), para que los 11 fletes
-- sean comparables en la misma moneda. Mobile/Savannah/Vancouver ya son $/t nativos.

select
    fecha_mes_fem                    as "Date 1",
    fecha_issue                      as "Date 2",
    pine_pulpwood_usd                as "Pine Pulpwood US South (US$/s.ton)",
    pine_chips_usd                   as "In-wood pine chips US South (US$/s.ton)",
    pine_residuals_usd               as "Pine process residuals US South (US$/s.ton)",
    sweden_eur_mwh                   as "Energy wood/biomass - Sweden DAT (€/MWh)",
    sweden_eur_gj                    as "Energy wood/biomass - Sweden DAT (€/GJ)",
    finland_eur_mwh                  as "Forest biomass - Finland DAT (€/MWh)",
    finland_eur_gj                   as "Forest biomass - Finland DAT (€/GJ)",
    lithuania_chips_eur_mwh          as "Wood chips - Lithunania SM2 (€/MWh)",
    lithuania_chips_eur_gj           as "Wood chips - FOB Lithunania SM2 (€/GJ)",
    chips_cif_nwe_eur_gj             as "Argus Biomass chips CIF NWE (€/GJ)",
    cif_nwe_usd_t                    as "Industrial Wood Pellet CIF NWE ($/t)",
    cif_nwe_eur_t                    as "Industrial Wood Pellet CIF NWE (€/t)",
    cif_nwe_eur_gj                   as "Industrial Wood Pellet CIF NWE (€/GJ)",
    fob_baltics_eur_t                as "Industrial Wood Pellet FOB BALTICS (€/t)",
    fob_baltics_eur_gj               as "Industrial Wood Pellet FOB BALTICS (€/GJ)",
    fob_portugal_eur_t               as "Industrial Wood Pellet FOB PORTUGAL (€/t)",
    fob_portugal_eur_gj              as "Industrial Wood Pellet FOB PORTUGAL (€/GJ)",
    endex_ancla_usd_t                as "Industrial Wood Pellet ENDEX CIF ARA ($/t)",
    endex_ancla_usd_gj               as "Industrial Wood Pellet ENDEX CIF ARA ($/GJ)",
    endex_ancla_usd_mwh              as "Industrial Wood Pellet ENDEX CIF ARA ($/MWh)",
    endex_ancla_eur_t                as "Industrial Wood Pellet ENDEX CIF ARA (€/t)",
    endex_ancla_eur_gj               as "Industrial Wood Pellet ENDEX CIF ARA (€/GJ)",
    endex_ancla_eur_mwh              as "Industrial Wood Pellet ENDEX CIF ARA (€/MWh)",
    bulk_mid_eur_t                   as "Residential pellet DAT Northern Italy in BULK (€/t)",
    bulk_mid_eur_gj                  as "Residential pellet DAT Northern Italy in BULK (€/GJ)",
    bulk_mid_eur_mwh                 as "Residential pellet DAT Northern Italy in BULK (€/MWh)",
    bagged_mid_eur_t                 as "Residential pellet DAT Northern Italy BAGGED (€/t)",
    bagged_mid_eur_gj                as "Residential pellet DAT Northern Italy BAGGED (€/GJ)",
    bagged_mid_eur_mwh               as "Residential pellet DAT Northern Italy BAGGED (€/MWh)",
    swiss_preis_eur_t                as "Residential Swiss Pellet Preis (€/t)",
    swiss_preis_eur_gj               as "Residential Swiss Pellet Preis (€/GJ)",
    swiss_preis_eur_mwh              as "Residential Swiss Pellet Preis (€/MWh)",
    germany_depi_eur_t               as "Residential Germany DEPI (€/t)",
    germany_depi_eur_gj              as "Residential Germany DEPI (€/GJ)",
    germany_depi_eur_mwh             as "Residential Germany DEPI (€/MWh)",
    austria_propellet_eur_t          as "Residential Austria ProPellet (€/t)",
    austria_propellet_eur_gj         as "Residential Austria ProPellet (€/GJ)",
    austria_propellet_eur_mwh        as "Residential Austria ProPellet (€/tMWh)",
    baltpool_eur_t                   as "Lithuania Batpool pellets UAB (€/t)",
    baltpool_eur_gj                  as "Lithuania Batpool pellets UAB (€/GJ)",
    baltpool_eur_mwh                 as "Lithuania Batpool pellets UAB (€/MWh)",
    viet_japan_fit_usd_t             as "Industrial wood pellet FOB Vietnam to Japan - FIT ($/t)",
    viet_japan_fit_eur_t             as "Industrial wood pellet FOB Vietnam to Japan - FIT (€/t)",
    viet_japan_fit_eur_gj            as "Industrial wood pellet FOB Vietnam to Japan - FIT (€/GJ)",
    viet_japan_fit_eur_mwh           as "Industrial wood pellet FOB Vietnam to Japan - FIT (€/MWh)",
    viet_korea_usd_t                 as "Industrial wood pellet FOB Vietnam to Korea ($/t)",
    viet_korea_eur_t                 as "Industrial wood pellet FOB Vietnam to Korea (€/t)",
    viet_korea_eur_gj                as "Industrial wood pellet FOB Vietnam to Korea (€/GJ)",
    viet_korea_eur_mwh               as "Industrial wood pellet FOB Vietnam to Korea (€/MWh)",
    gwangyang_usd_t                  as "Industrial wood pellet CFR Gwangyang ($/t)",
    gwangyang_eur_t                  as "Industrial wood pellet CFR Gwangyang (€/t)",
    gwangyang_eur_gj                 as "Industrial wood pellet CFR Gwangyang (€/GJ)",
    gwangyang_eur_mwh                as "Industrial wood pellet CFR Gwangyang (€/MWh)",
    -- fletes Aveiro y Riga: EUROS (el sheet ponia $/t por error)
    aveiro_ara_usd_t                 as "Pellet Freights 3500t (Aveiro-NWE) $/t",
    aveiro_cph_usd_t                 as "Pellet Freights 3500t (Aveiro-CPH) $/t",
    aveiro_hull_usd_t                as "Pellet Freights 3500t (Aveiro-Hull) $/t",
    riga_ara_usd_t                   as "Pellet Freights 5000t (Riga-ARA) $/t",
    riga_cph_usd_t                   as "Pellet Freights 5000t (Riga-CPH) $/t",
    riga_stockholm_usd_t             as "Pellet Freights 5000t (Riga-Stockholm) $/t",
    -- fletes transatlanticos: DOLARES (correcto en el sheet)
    mobile_ara_25kt_usd_t            as "Pellet Freights 25000t (Mobile-ARA) $/t",
    mobile_ara_45kt_usd_t            as "Pellet Freights 45000t (Mobile-ARA) $/t",
    savannah_ara_25kt_usd_t          as "Pellet Freights 25000t (Savannah-ARA) $/t",
    savannah_ara_45kt_usd_t          as "Pellet Freights 45000t (Savannah-ARA) $/t",
    vancouver_ara_45kt_usd_t         as "Pellet Freights 45000t (Vancouvert-ARA) $/t",
    sumatra_fit_usd_t                as "Asian PKS FOB East Coast Sumatra to Japan-FIT ($/t)",
    sumatra_usd_t                    as "Asian PKS FOB East Coast Sumatra ($/t)",
    malaysia_fit_usd_t               as "Asian PKS FOB Peninsular Malaysia to Japan-FIT ($/t)",
    malaysia_usd_t                   as "Asian PKS FOB Peninsular Malaysia ($/t)"

from "postgres"."analytics"."foto_semanal"
order by fecha_issue
  );
  