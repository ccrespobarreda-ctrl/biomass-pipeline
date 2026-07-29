
    
    



select endex_ancla_eur_t
from (select * from "postgres"."analytics"."fem_mensual_final" where mes >= '2025-01-01') dbt_subquery
where endex_ancla_eur_t is null


