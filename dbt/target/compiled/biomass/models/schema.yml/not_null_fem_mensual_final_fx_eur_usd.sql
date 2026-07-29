
    
    



select fx_eur_usd
from (select * from "postgres"."analytics"."fem_mensual_final" where mes >= '2025-01-01') dbt_subquery
where fx_eur_usd is null


