import pandas as pd


def filter_sales(sales, start_date, end_date, category="All categories"):
    if start_date > end_date:
        raise ValueError("Start date must not be after end date.")
    matches = sales["sales_date"].dt.date.between(start_date, end_date)
    if category != "All categories":
        matches &= sales["category"].eq(category)
    return sales.loc[matches].copy()


def sales_summary(sales):
    orders = int(sales["transaction_id"].nunique())
    revenue = float(sales["revenue"].sum())
    return {
        "revenue": revenue,
        "orders": orders,
        "average_order_value": revenue / orders if orders else 0,
        "units": int(sales["quantity"].sum()),
    }


def revenue_trend(sales):
    if sales.empty:
        return pd.DataFrame(columns=["sales_date", "revenue"])
    return sales.resample("D", on="sales_date")["revenue"].sum().reset_index()


def product_performance(sales, products, as_of, category="All categories"):
    """Summarize selected sales against the catalog, including zero-sale products."""
    totals = sales.groupby("product_id").agg(
        units=("quantity", "sum"),
        revenue=("revenue", "sum"),
        orders=("transaction_id", "nunique"),
        last_sale=("sales_date", "max"),
    )
    result = products.merge(totals, on="product_id", how="left", validate="one_to_one")
    result[["units", "revenue", "orders"]] = result[["units", "revenue", "orders"]].fillna(0)
    result[["units", "orders"]] = result[["units", "orders"]].astype(int)
    result["days_since_sale"] = (pd.Timestamp(as_of) - result["last_sale"]).dt.days.astype("Int64")
    result["slow_mover"] = (
        result["units"].le(5)
        | result["days_since_sale"].ge(30).fillna(False)
        | result["last_sale"].isna()
    )
    if category != "All categories":
        result = result.loc[result["category"].eq(category)]
    return result.reset_index(drop=True)


def rank_products(performance, by="revenue"):
    return performance.sort_values([by, "product_name"], ascending=[False, True]).reset_index(drop=True)


def filter_rules(rules, scope="All orders", min_support=0.05, min_confidence=0.5, min_lift=1.0):
    """Filter fixed illustrative examples, always excluding lift at or below one."""
    matches = (
        rules["scope"].eq(scope)
        & rules["support"].ge(min_support)
        & rules["confidence"].ge(min_confidence)
        & rules["lift"].ge(min_lift)
        & rules["lift"].gt(1)
    )
    return rules.loc[matches].sort_values(
        ["lift", "confidence", "rule_id"], ascending=[False, False, True]
    ).reset_index(drop=True)
