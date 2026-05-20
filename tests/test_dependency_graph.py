"""Tests for SQLGlot-backed dependency graph extraction."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.graph.dependencies import (  # noqa: E402
    _find_cycle_nodes,
    build_dependency_graph,
)


def test_dependency_graph_for_one_cte_reading_one_table() -> None:
    result = build_dependency_graph(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
        )
        SELECT user_id
        FROM active_users
        """
    )

    assert result["has_parse_error"] is False
    assert result["nodes"] == [
        {"name": "active_users", "node_type": "cte"},
        {"name": "users", "node_type": "table"},
    ]
    assert result["edges"] == [
        {
            "from": "active_users",
            "to": "users",
            "dependency_type": "cte_to_table",
        }
    ]
    assert result["cte_count"] == 1
    assert result["table_count"] == 1


def test_dependency_graph_for_two_ctes_with_cte_dependency() -> None:
    result = build_dependency_graph(
        """
        WITH base_customers AS (
            SELECT customer_id
            FROM customers
        ),
        customer_orders AS (
            SELECT base_customers.customer_id, orders.order_id
            FROM base_customers
            JOIN orders ON orders.customer_id = base_customers.customer_id
        )
        SELECT customer_id
        FROM customer_orders
        """
    )

    assert {
        "from": "customer_orders",
        "to": "base_customers",
        "dependency_type": "cte_to_cte",
    } in result["edges"]
    assert {
        "from": "customer_orders",
        "to": "orders",
        "dependency_type": "cte_to_table",
    } in result["edges"]
    assert result["has_cycle"] is False


def test_dependency_graph_for_multiple_ctes_and_tables() -> None:
    result = build_dependency_graph(
        """
        WITH user_orders AS (
            SELECT user_id, order_id
            FROM orders
        ),
        order_payments AS (
            SELECT user_orders.order_id, payments.payment_id
            FROM user_orders
            JOIN payments ON payments.order_id = user_orders.order_id
        ),
        purchased_products AS (
            SELECT order_payments.order_id, products.product_id
            FROM order_payments
            JOIN products ON products.product_id = order_payments.payment_id
        )
        SELECT product_id
        FROM purchased_products
        """
    )

    assert result["cte_count"] == 3
    assert result["table_count"] == 3
    assert {"name": "orders", "node_type": "table"} in result["nodes"]
    assert {"name": "payments", "node_type": "table"} in result["nodes"]
    assert {"name": "products", "node_type": "table"} in result["nodes"]
    assert {
        "from": "purchased_products",
        "to": "order_payments",
        "dependency_type": "cte_to_cte",
    } in result["edges"]


def test_dependency_graph_without_ctes_captures_table_nodes() -> None:
    result = build_dependency_graph("SELECT product_id FROM products")

    assert result["has_parse_error"] is False
    assert result["cte_count"] == 0
    assert result["table_count"] == 1
    assert result["nodes"] == [{"name": "products", "node_type": "table"}]
    assert result["edges"] == []


def test_dependency_graph_handles_invalid_sql_without_raising() -> None:
    result = build_dependency_graph("WITH broken AS (SELECT * FROM")

    assert result["has_parse_error"] is True
    assert result["nodes"] == []
    assert result["edges"] == []
    assert result["error_message"]


def test_dependency_graph_supports_explicit_postgres_dialect() -> None:
    result = build_dependency_graph(
        """
        WITH current_users AS (
            SELECT user_id, NOW()::DATE AS current_date
            FROM users
        )
        SELECT user_id
        FROM current_users
        """,
        dialect="postgres",
    )

    assert result["dialect"] == "postgres"
    assert result["has_parse_error"] is False
    assert {"name": "current_users", "node_type": "cte"} in result["nodes"]


def test_cycle_detector_reports_simple_cycle() -> None:
    edges = [
        {"from": "first_cte", "to": "second_cte", "dependency_type": "cte_to_cte"},
        {"from": "second_cte", "to": "first_cte", "dependency_type": "cte_to_cte"},
    ]

    assert _find_cycle_nodes(edges) == ["first_cte", "second_cte"]
