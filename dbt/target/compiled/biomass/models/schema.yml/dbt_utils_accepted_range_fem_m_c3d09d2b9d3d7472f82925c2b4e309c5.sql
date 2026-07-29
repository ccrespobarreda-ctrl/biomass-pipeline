

with meet_condition as(
  select *
  from "postgres"."analytics"."fem_mensual_final"
),

validation_errors as (
  select *
  from meet_condition
  where
    -- never true, defaults to an empty result set. Exists to ensure any combo of the `or` clauses below succeeds
    1 = 2
    -- records with a value >= min_value are permitted. The `not` flips this to find records that don't meet the rule.
    or not endex_ancla_eur_t >= 100
    -- records with a value <= max_value are permitted. The `not` flips this to find records that don't meet the rule.
    or not endex_ancla_eur_t <= 400
)

select *
from validation_errors

