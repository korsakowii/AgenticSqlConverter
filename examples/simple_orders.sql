WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    order_count,
    total_spent
FROM customer_orders
WHERE total_spent > 100;
