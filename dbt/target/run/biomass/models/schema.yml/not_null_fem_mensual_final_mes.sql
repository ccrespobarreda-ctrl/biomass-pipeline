
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select mes
from "postgres"."analytics"."fem_mensual_final"
where mes is null



  
  
      
    ) dbt_internal_test