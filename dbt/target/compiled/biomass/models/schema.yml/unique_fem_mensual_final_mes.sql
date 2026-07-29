
    
    

select
    mes as unique_field,
    count(*) as n_records

from "postgres"."analytics"."fem_mensual_final"
where mes is not null
group by mes
having count(*) > 1


