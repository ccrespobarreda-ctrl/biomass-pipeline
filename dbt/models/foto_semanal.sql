-- Foto semanal: una fila por miercoles del Argus, con el dato del FEM
-- del mes correspondiente "arrastrado" a esa semana.
-- Version inicial reducida: ampliaremos columnas cuando confirmemos el arrastre.

select
    a.fecha_issue,
    -- datos semanales del Argus
    a.cif_nwe_usd_t,
    a.fob_baltics_eur_t,
    -- datos mensuales del FEM, arrastrados a esta semana segun su mes
    f.germany_depi_eur_t,
    f.endex_ancla_eur_t,
    f.finland_eur_mwh
from argus_semanal a
left join {{ ref('fem_mensual_final') }} f
    on date_trunc('month', a.fecha_issue) = f.mes
order by a.fecha_issue