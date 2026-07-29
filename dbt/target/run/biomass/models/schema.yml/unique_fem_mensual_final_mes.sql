
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    mes as unique_field,
    count(*) as n_records

from "postgres"."analytics"."fem_mensual_final"
where mes is not null
group by mes
having count(*) > 1



  
  
      
    ) dbt_internal_test