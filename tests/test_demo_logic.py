from datetime import date

import pandas as pd
import pytest

from src.demo_data import load_products, load_sales
from src.demo_logic import filter_rules, filter_sales, product_performance, rank_products, revenue_trend, sales_summary


@pytest.fixture
def sales():
    return pd.DataFrame(
        {
            "transaction_id": ["A", "A", "B", "C"],
            "product_id": ["P1", "P2", "P1", "P2"],
            "category": ["Home", "Pantry", "Home", "Pantry"],
            "quantity": [2, 1, 1, 2],
            "unit_price": [100, 50, 100, 50],
            "revenue": [200, 50, 100, 100],
            "sales_date": pd.to_datetime(["2026-07-01", "2026-07-01", "2026-07-03", "2026-07-03"]),
        }
    )


def test_sales_summary_counts_baskets_not_product_lines(sales):
    assert sales_summary(sales) == {
        "revenue": 450,
        "orders": 3,
        "average_order_value": 150,
        "units": 6,
    }


def test_sales_filters_are_inclusive_and_do_not_mutate_input(sales):
    original = sales.copy(deep=True)
    result = filter_sales(sales, date(2026, 7, 3), date(2026, 7, 3), "Home")

    assert result["transaction_id"].tolist() == ["B"]
    pd.testing.assert_frame_equal(sales, original)


def test_no_matching_sales_have_zero_summary(sales):
    result = filter_sales(sales, date(2026, 8, 1), date(2026, 8, 31))

    assert result.empty
    assert sales_summary(result) == {
        "revenue": 0,
        "orders": 0,
        "average_order_value": 0,
        "units": 0,
    }
    assert revenue_trend(result).empty


def test_reversed_dates_are_rejected(sales):
    with pytest.raises(ValueError, match="Start date"):
        filter_sales(sales, date(2026, 7, 3), date(2026, 7, 1))


def test_revenue_trend_sums_lines_and_includes_zero_sales_days(sales):
    trend = revenue_trend(sales)

    assert trend["sales_date"].dt.date.tolist() == [date(2026, 7, 1), date(2026, 7, 2), date(2026, 7, 3)]
    assert trend["revenue"].tolist() == [250, 0, 200]


def test_demo_data_is_deterministic_and_uses_one_catalog():
    products = load_products()
    sales = load_sales()

    pd.testing.assert_frame_equal(sales, load_sales())
    assert products["product_id"].is_unique
    assert set(sales["product_id"]) <= set(products["product_id"])
    assert (sales["revenue"] == sales["quantity"] * sales["unit_price"]).all()
    assert sales["transaction_id"].nunique() == 120
    assert sales["sales_date"].min().date() == date(2026, 7, 1)
    assert sales["sales_date"].max().date() == date(2026, 9, 30)


def test_product_performance_aggregates_orders_and_includes_unsold_products(sales):
    products = pd.DataFrame(
        [("P1", "Mug", "Home", 100), ("P2", "Coffee", "Pantry", 50), ("P3", "Tray", "Home", 75)],
        columns=["product_id", "product_name", "category", "unit_price"],
    )
    result = product_performance(sales, products, date(2026, 8, 3)).set_index("product_id")

    assert result.loc["P1", "units"] == 3
    assert result.loc["P1", "orders"] == 2
    assert result.loc["P1", "revenue"] == 300
    assert result.loc["P1", "days_since_sale"] == 31
    assert result.loc["P3", "units"] == 0
    assert pd.isna(result.loc["P3", "last_sale"])
    assert result.loc["P3", "slow_mover"]


def test_product_category_filter_keeps_only_matching_catalog_products(sales):
    products = pd.DataFrame(
        [("P1", "Mug", "Home", 100), ("P2", "Coffee", "Pantry", 50)],
        columns=["product_id", "product_name", "category", "unit_price"],
    )
    selected = filter_sales(sales, date(2026, 7, 1), date(2026, 7, 3), "Home")
    result = product_performance(selected, products, date(2026, 7, 3), "Home")

    assert result["product_id"].tolist() == ["P1"]


def test_slow_mover_flags_use_selected_period_end_not_current_date():
    products = load_products()
    result = product_performance(load_sales(), products, date(2026, 9, 30)).set_index("product_id")

    assert result.loc["P006", "slow_mover"]
    assert result.loc["P008", "slow_mover"]
    assert not result.loc["P002", "slow_mover"]


def test_rankings_switch_between_revenue_and_units_without_mutation():
    performance = pd.DataFrame(
        {"product_name": ["Mug", "Coffee"], "revenue": [300, 500], "units": [8, 4]}
    )
    original = performance.copy(deep=True)

    assert rank_products(performance, "revenue")["product_name"].tolist() == ["Coffee", "Mug"]
    assert rank_products(performance, "units")["product_name"].tolist() == ["Mug", "Coffee"]
    pd.testing.assert_frame_equal(performance, original)


def test_empty_period_product_performance_has_no_sales():
    sales = load_sales().iloc[:0]
    result = product_performance(sales, load_products(), date(2026, 9, 30))

    assert (result["revenue"] == 0).all()
    assert (result["orders"] == 0).all()
    assert result["slow_mover"].all()


def test_rule_thresholds_are_inclusive_but_lift_one_is_always_excluded():
    rules = pd.DataFrame(
        [
            ("A", "All orders", 0.05, 0.5, 2.0),
            ("B", "All orders", 0.25, 1.0, 1.0),
            ("C", "All orders", 0.049, 0.5, 2.0),
            ("D", "All orders", 0.1, 0.499, 2.0),
            ("E", "Steady performers", 0.5, 1.0, 3.0),
        ],
        columns=["rule_id", "scope", "support", "confidence", "lift"],
    )
    original = rules.copy(deep=True)
    result = filter_rules(rules, "All orders", min_support=0.05, min_confidence=0.5, min_lift=2.0)

    assert result["rule_id"].tolist() == ["A"]
    assert "B" not in filter_rules(rules, "All orders", min_lift=1.0)["rule_id"].tolist()
    pd.testing.assert_frame_equal(rules, original)


def test_rule_filter_orders_strongest_examples_first_and_handles_empty_results():
    rules = pd.DataFrame(
        [("A", "All orders", 0.2, 0.6, 2.0), ("B", "All orders", 0.3, 0.9, 2.0)],
        columns=["rule_id", "scope", "support", "confidence", "lift"],
    )

    assert filter_rules(rules, "All orders")["rule_id"].tolist() == ["B", "A"]
    assert filter_rules(rules, "All orders", min_lift=3.0).empty
