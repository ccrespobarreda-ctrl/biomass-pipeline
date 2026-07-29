
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select endex_ancla_eur_t
from (select * from "postgres"."analytics"."fem_mensual_final" where mes >= '2025-01-01') dbt_subquery
where endex_ancla_eur_t is null



  
  
      
    ) dbt_internal_test