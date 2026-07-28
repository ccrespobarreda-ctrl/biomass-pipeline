
  
    

  create  table "postgres"."analytics"."fem_mensual_final__dbt_tmp"
  
  
    as
  
  (
    -- Valor bueno de cada mes del FEM: la version del issue mas reciente.
-- Asi los meses que se rellenaron en issues posteriores se quedan con su valor final.
select distinct on (mes)
    mes,
    germany_depi_eur_t,
    austria_propellet_eur_t,
    swiss_preis_eur_t,
    baltpool_eur_t,
    endex_ancla_eur_t,
    finland_eur_mwh,
    sweden_eur_mwh,
    pine_pulpwood_usd,
    pine_chips_usd,
    pine_residuals_usd,
    lithuania_chips_eur_mwh
from fem_mensual
order by mes, issue_origen desc
  );
  