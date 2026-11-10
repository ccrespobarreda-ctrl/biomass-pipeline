-- Test singular: coherencia INTERNA de foto_publicacion, usando solo lo que
-- afirman las ETIQUETAS de las columnas (no el mapeo tecnico).
--
-- Por que asi: un test que comparase columna a columna contra foto_semanal
-- tendria que repetir el mismo mapeo, asi que un emparejamiento equivocado
-- pasaria desapercibido. Comprobando las proporciones que implican las etiquetas,
-- un cruce (p.ej. un BAGGED publicado bajo una etiqueta BULK) SI se detecta.
--
-- Reglas: (a) /GJ = /t / 17 ; (b) /MWh = /GJ * 3.6 ; (c) /GJ = /MWh / 3.6 ;
--         (d) el cociente €/$ debe ser el MISMO en todas las series de la fila.
-- dbt: el test PASA si esta consulta no devuelve filas.

with p as (select * from {{ ref('foto_publicacion') }}),

proporciones as (
    select "Date 2" as fecha, 'CIF NWE €/GJ = €/t / 17' as regla,
           "Industrial Wood Pellet CIF NWE (€/t)" as origen, "Industrial Wood Pellet CIF NWE (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2" as fecha, 'FOB BALTICS €/GJ = €/t / 17' as regla,
           "Industrial Wood Pellet FOB BALTICS (€/t)" as origen, "Industrial Wood Pellet FOB BALTICS (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2" as fecha, 'FOB PORTUGAL €/GJ = €/t / 17' as regla,
           "Industrial Wood Pellet FOB PORTUGAL (€/t)" as origen, "Industrial Wood Pellet FOB PORTUGAL (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2" as fecha, 'ENDEX EUR €/GJ = €/t / 17' as regla,
           "Industrial Wood Pellet ENDEX CIF ARA (€/t)" as origen, "Industrial Wood Pellet ENDEX CIF ARA (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'ENDEX EUR €/MWh = €/GJ * 3.6',
           "Industrial Wood Pellet ENDEX CIF ARA (€/GJ)", "Industrial Wood Pellet ENDEX CIF ARA (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'ENDEX USD $/GJ = $/t / 17' as regla,
           "Industrial Wood Pellet ENDEX CIF ARA ($/t)" as origen, "Industrial Wood Pellet ENDEX CIF ARA ($/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'ENDEX USD $/MWh = $/GJ * 3.6',
           "Industrial Wood Pellet ENDEX CIF ARA ($/GJ)", "Industrial Wood Pellet ENDEX CIF ARA ($/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Italy BULK €/GJ = €/t / 17' as regla,
           "Residential pellet DAT Northern Italy in BULK (€/t)" as origen, "Residential pellet DAT Northern Italy in BULK (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Italy BULK €/MWh = €/GJ * 3.6',
           "Residential pellet DAT Northern Italy in BULK (€/GJ)", "Residential pellet DAT Northern Italy in BULK (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Italy BAGGED €/GJ = €/t / 17' as regla,
           "Residential pellet DAT Northern Italy BAGGED (€/t)" as origen, "Residential pellet DAT Northern Italy BAGGED (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Italy BAGGED €/MWh = €/GJ * 3.6',
           "Residential pellet DAT Northern Italy BAGGED (€/GJ)", "Residential pellet DAT Northern Italy BAGGED (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Swiss €/GJ = €/t / 17' as regla,
           "Residential Swiss Pellet Preis (€/t)" as origen, "Residential Swiss Pellet Preis (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Swiss €/MWh = €/GJ * 3.6',
           "Residential Swiss Pellet Preis (€/GJ)", "Residential Swiss Pellet Preis (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Germany DEPI €/GJ = €/t / 17' as regla,
           "Residential Germany DEPI (€/t)" as origen, "Residential Germany DEPI (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Germany DEPI €/MWh = €/GJ * 3.6',
           "Residential Germany DEPI (€/GJ)", "Residential Germany DEPI (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Austria €/GJ = €/t / 17' as regla,
           "Residential Austria ProPellet (€/t)" as origen, "Residential Austria ProPellet (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Austria €/MWh = €/GJ * 3.6',
           "Residential Austria ProPellet (€/GJ)", "Residential Austria ProPellet (€/tMWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Baltpool €/GJ = €/t / 17' as regla,
           "Lithuania Batpool pellets UAB (€/t)" as origen, "Lithuania Batpool pellets UAB (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Baltpool €/MWh = €/GJ * 3.6',
           "Lithuania Batpool pellets UAB (€/GJ)", "Lithuania Batpool pellets UAB (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Viet Japan FIT €/GJ = €/t / 17' as regla,
           "Industrial wood pellet FOB Vietnam to Japan - FIT (€/t)" as origen, "Industrial wood pellet FOB Vietnam to Japan - FIT (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Viet Japan FIT €/MWh = €/GJ * 3.6',
           "Industrial wood pellet FOB Vietnam to Japan - FIT (€/GJ)", "Industrial wood pellet FOB Vietnam to Japan - FIT (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Viet Korea €/GJ = €/t / 17' as regla,
           "Industrial wood pellet FOB Vietnam to Korea (€/t)" as origen, "Industrial wood pellet FOB Vietnam to Korea (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Viet Korea €/MWh = €/GJ * 3.6',
           "Industrial wood pellet FOB Vietnam to Korea (€/GJ)", "Industrial wood pellet FOB Vietnam to Korea (€/MWh)",
           3.6 from p
    union all
    select "Date 2" as fecha, 'Gwangyang €/GJ = €/t / 17' as regla,
           "Industrial wood pellet CFR Gwangyang (€/t)" as origen, "Industrial wood pellet CFR Gwangyang (€/GJ)" as calculado,
           1.0/17 as factor from p
    union all
    select "Date 2", 'Gwangyang €/MWh = €/GJ * 3.6',
           "Industrial wood pellet CFR Gwangyang (€/GJ)", "Industrial wood pellet CFR Gwangyang (€/MWh)",
           3.6 from p
    union all
    select "Date 2", 'Sweden €/GJ = €/MWh / 3.6',
           "Energy wood/biomass - Sweden DAT (€/MWh)", "Energy wood/biomass - Sweden DAT (€/GJ)",
           1.0/3.6 from p
    union all
    select "Date 2", 'Finland €/GJ = €/MWh / 3.6',
           "Forest biomass - Finland DAT (€/MWh)", "Forest biomass - Finland DAT (€/GJ)",
           1.0/3.6 from p
    union all
    select "Date 2", 'Lithuania chips €/GJ = €/MWh / 3.6',
           "Wood chips - Lithunania SM2 (€/MWh)", "Wood chips - FOB Lithunania SM2 (€/GJ)",
           1.0/3.6 from p
),

fallos_proporcion as (
    select fecha, regla, origen, calculado
    from proporciones
    where origen is not null and calculado is not null
      and abs(calculado - origen * factor) > 0.05
),

-- tipo de cambio implicito en cada serie que se publica en las dos monedas
cambios as (
    select "Date 2" as fecha, 'CIF NWE' as serie,
           round("Industrial Wood Pellet CIF NWE (€/t)" / nullif("Industrial Wood Pellet CIF NWE ($/t)", 0), 4) as fx from p
    union all
    select "Date 2" as fecha, 'ENDEX' as serie,
           round("Industrial Wood Pellet ENDEX CIF ARA (€/t)" / nullif("Industrial Wood Pellet ENDEX CIF ARA ($/t)", 0), 4) as fx from p
    union all
    select "Date 2" as fecha, 'Viet Japan FIT' as serie,
           round("Industrial wood pellet FOB Vietnam to Japan - FIT (€/t)" / nullif("Industrial wood pellet FOB Vietnam to Japan - FIT ($/t)", 0), 4) as fx from p
    union all
    select "Date 2" as fecha, 'Viet Korea' as serie,
           round("Industrial wood pellet FOB Vietnam to Korea (€/t)" / nullif("Industrial wood pellet FOB Vietnam to Korea ($/t)", 0), 4) as fx from p
    union all
    select "Date 2" as fecha, 'Gwangyang' as serie,
           round("Industrial wood pellet CFR Gwangyang (€/t)" / nullif("Industrial wood pellet CFR Gwangyang ($/t)", 0), 4) as fx from p
),

fallos_cambio as (
    -- en una misma fecha, todas las series deben implicar el mismo cambio
    select fecha, 'cambio €/$ incoherente entre series' as regla,
           min(fx) as origen, max(fx) as calculado
    from cambios
    where fx is not null
    group by fecha
    having max(fx) - min(fx) > 0.01
)

select * from fallos_proporcion
union all
select * from fallos_cambio
