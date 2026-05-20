-- Synthetic SQL for local migration-validation demos only.
-- No proprietary tables, schemas, credentials, or live systems.

WITH bounds AS (
    SELECT CURRENT_DATE AS as_of_date
),

base_events AS (
    SELECT
        geography_key,
        occurred_at::date AS event_calendar_date,
        product_key,
        quantity_value,
        CASE
            WHEN quantity_value >= 100 THEN quantity_value
            ELSE NULL
        END AS large_line_quantity
    FROM metric_fact_sample
),

geo_keys AS (
    SELECT DISTINCT geography_key
    FROM base_events
),

product_keys AS (
    SELECT DISTINCT product_key
    FROM base_events
),

geo_enriched AS (
    SELECT
        b.geography_key,
        b.event_calendar_date,
        b.product_key,
        SUM(b.quantity_value) AS total_quantity_value,
        MAX(b.large_line_quantity) AS peak_line_quantity
    FROM base_events AS b
    INNER JOIN geography_dim_sample AS g
        ON g.geography_key = b.geography_key
    WHERE b.event_calendar_date IS NOT NULL
    GROUP BY b.geography_key, b.event_calendar_date, b.product_key
),

product_enriched AS (
    SELECT
        geo_enriched.*,
        p.category_label
    FROM geo_enriched
    INNER JOIN product_dim_sample AS p
        ON p.product_key = geo_enriched.product_key
)

SELECT
    category_label,
    SUM(total_quantity_value) AS total_units,
    AVG(peak_line_quantity) AS average_peak_units
FROM product_enriched
GROUP BY category_label;
