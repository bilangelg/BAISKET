from datetime import date, timedelta

import pandas as pd


def load_products():
    """Return a fresh copy of the fictional shop's catalog; prices are in PHP."""
    return pd.DataFrame(
        [
            ("P001", "Ceramic Mug", "Home & Living", 249),
            ("P002", "Coffee Beans", "Pantry", 349),
            ("P003", "Desk Notebook", "Stationery", 129),
            ("P004", "Gel Pen Set", "Stationery", 89),
            ("P005", "Cotton Tote", "Accessories", 199),
            ("P006", "Scented Candle", "Home & Living", 299),
            ("P007", "Bamboo Coaster", "Home & Living", 79),
            ("P008", "Desk Organizer", "Home & Living", 399),
        ],
        columns=["product_id", "product_name", "category", "unit_price"],
    )


def load_sales():
    """Build 120 repeatable sample orders across July–September 2026."""
    patterns = [
        ["P001", "P002", "P007"],
        ["P003", "P004"],
        ["P002"],
        ["P001", "P005"],
        ["P003", "P004", "P005"],
        ["P001", "P007"],
        ["P002", "P003"],
        ["P005"],
    ]
    records = []
    for index in range(120):
        basket = list(patterns[index % len(patterns)])
        if index < 20 and index % 6 == 0:
            basket.append("P006")
        if index < 4:
            basket.append("P008")
        for position, product_id in enumerate(basket):
            records.append(
                {
                    "transaction_id": f"DEMO-{index + 1:03d}",
                    "product_id": product_id,
                    "quantity": 1 + (index + position) % 3,
                    "sales_date": date(2026, 7, 1) + timedelta(days=index * 91 // 119),
                }
            )
    sales = pd.DataFrame(records).merge(load_products(), on="product_id", validate="many_to_one")
    sales["sales_date"] = pd.to_datetime(sales["sales_date"])
    sales["revenue"] = sales["quantity"] * sales["unit_price"]
    return sales


def load_cluster_membership(algorithm="K-means"):
    """Return hand-assigned storyboard labels, not the output of a model."""
    scenarios = {
        "K-means": {
            "Top sellers": ["P001", "P002", "P005"],
            "Steady performers": ["P003", "P004", "P007"],
            "Slow movers": ["P006", "P008"],
        },
        "DBSCAN": {
            "Core sellers": ["P001", "P002", "P005"],
            "Everyday essentials": ["P003", "P004", "P007"],
            "Outliers": ["P006", "P008"],
        },
    }
    return pd.DataFrame(
        [(product_id, cluster) for cluster, ids in scenarios[algorithm].items() for product_id in ids],
        columns=["product_id", "cluster"],
    )


def load_rule_scopes():
    """Fixed basket counts for the full sample and K-means storyboard segments."""
    return {"All orders": 120, "Top sellers": 105, "Steady performers": 75, "Slow movers": 7}


def load_association_rules():
    """Return curated examples with fixed metrics; no Apriori or mining runs.

    Fractions match the bundled baskets for consistency, not model validation.
    Segment scopes include only orders with at least one member product.
    Low-lift examples intentionally exercise the recommendation empty states.
    """
    return pd.DataFrame(
        [
            ("R001", "All orders", "P003", "P004", 1 / 4, 2 / 3, 8 / 3, "Bundle"),
            ("R002", "All orders", "P004", "P003", 1 / 4, 1, 8 / 3, "Cross-sell"),
            ("R003", "All orders", "P001", "P007", 1 / 4, 2 / 3, 8 / 3, "Bundle"),
            ("R004", "All orders", "P007", "P001", 1 / 4, 1, 8 / 3, "Cross-sell"),
            ("R005", "All orders", "P007", "P002", 1 / 8, 1 / 2, 4 / 3, "Cross-sell"),
            ("R006", "All orders", "P002", "P007", 1 / 8, 1 / 3, 4 / 3, "Cross-sell"),
            ("R007", "All orders", "P001", "P002", 1 / 8, 1 / 3, 8 / 9, "Cross-sell"),
            ("R008", "All orders", "P006", "P008", 1 / 120, 1 / 4, 15 / 2, "Bundle"),
            ("R009", "Steady performers", "P003", "P004", 2 / 5, 2 / 3, 5 / 3, "Bundle"),
            ("R010", "Steady performers", "P004", "P003", 2 / 5, 1, 5 / 3, "Cross-sell"),
            ("R011", "Top sellers", "P001", "P002", 1 / 7, 1 / 3, 7 / 9, "Cross-sell"),
            ("R012", "Slow movers", "P006", "P008", 1 / 7, 1 / 4, 7 / 16, "Bundle"),
        ],
        columns=["rule_id", "scope", "antecedent_id", "consequent_id", "support", "confidence", "lift", "suggestion"],
    )
