import pandas as pd
import plotly.express as px
import streamlit as st

from src.demo_data import load_products, load_sales
from src.demo_logic import filter_sales, product_performance, rank_products


def render_products():
    sales, products = load_sales(), load_products()
    st.title("Product Analysis")
    st.caption("Understand your best sellers and the products that need attention. Sample prices are in PHP.")
    with st.container(border=True):
        period_column, category_column = st.columns([2, 1])
        with period_column:
            dates = st.date_input(
                "Sales period",
                value=(sales["sales_date"].min().date(), sales["sales_date"].max().date()),
                key="products_dates",
                format="DD/MM/YYYY",
            )
        with category_column:
            category = st.selectbox(
                "Product category",
                ["All categories", *sorted(products["category"].unique())],
                key="products_category",
            )
    if len(dates) != 2:
        st.info("Choose an end date to complete your sales period.")
        return
    filtered = filter_sales(sales, dates[0], dates[1], category)
    if filtered.empty:
        st.info("No sales match these filters. Try another period or category.")
        return

    performance = product_performance(filtered, products, dates[1], category)
    st.header("Product rankings")
    ranking = st.radio("Rank products by", ["Revenue", "Units sold"], horizontal=True, key="product_ranking")
    by = "revenue" if ranking == "Revenue" else "units"
    ranked = rank_products(performance, by)
    chart = px.bar(
        ranked,
        x=by,
        y="product_name",
        orientation="h",
        labels={"product_name": "Product", "revenue": "Revenue (PHP)", "units": "Units sold"},
        color_discrete_sequence=[st.get_option("theme.primaryColor")],
    )
    chart.update_layout(margin=dict(l=0, r=0, t=16, b=0), height=350)
    chart.update_yaxes(categoryorder="array", categoryarray=ranked["product_name"].tolist(), autorange="reversed")
    value_template = "Revenue: ₱%{x:,.2f}" if by == "revenue" else "Units sold: %{x:,d}"
    chart.update_traces(hovertemplate=f"<b>%{{y}}</b><br>{value_template}<extra></extra>")
    chart.update_xaxes(tickformat=",.0f" if by == "revenue" else ",d")
    st.plotly_chart(
        chart,
        width="stretch",
        config={"displaylogo": False, "scrollZoom": False},
        alt=f"Sample products ranked from highest to lowest {ranking.lower()} for the selected sales.",
    )
    table = ranked[["product_name", "category", "units", "revenue", "orders"]].rename(
        columns={"product_name": "Product", "category": "Category", "units": "Units sold", "revenue": "Revenue (PHP)", "orders": "Orders"}
    )
    st.caption("On narrow screens, scroll tables sideways for all columns, or inspect a product below.")
    st.dataframe(
        table,
        column_config={"Revenue (PHP)": st.column_config.NumberColumn(format="₱%,.2f")},
        hide_index=True, width="stretch", alt="Product rankings underlying the chart.",
    )

    st.header("Product details")
    names = products.set_index("product_id")["product_name"].to_dict()
    selected = st.selectbox(
        "Inspect a product", ranked["product_id"].tolist(),
        format_func=names.get, key="product_detail",
    )
    product = performance.set_index("product_id").loc[selected]
    with st.container(border=True):
        st.subheader(product["product_name"])
        st.caption(f"{product['category']} · {selected} · Sample unit price: ₱{product['unit_price']:,.2f}")
        with st.container(horizontal=True):
            for label, value in zip(
                ["Units sold", "Revenue", "Orders"],
                [str(product["units"]), f"₱{product['revenue']:,.2f}", str(product["orders"])],
            ):
                st.metric(label, value, width=180)
        if pd.isna(product["last_sale"]):
            st.caption("No matching sale in the selected period.")
        else:
            st.caption(f"Last matching sale: {product['last_sale']:%d %b %Y} · Days before period end: {product['days_since_sale']}.")
        if product["slow_mover"]:
            st.warning("Slow mover in this selection — an illustrative flag, not an inventory or stock alert.")

    st.header("Category performance")
    categories = (
        performance.groupby("category", as_index=False)[["units", "revenue"]]
        .sum().sort_values("revenue", ascending=False)
        .rename(columns={"category": "Category", "units": "Units sold", "revenue": "Revenue (PHP)"})
    )
    st.dataframe(
        categories,
        column_config={"Revenue (PHP)": st.column_config.NumberColumn(format="₱%,.2f")},
        hide_index=True, width="stretch", alt="Sample revenue and units sold by product category.",
    )

    st.header("Slow movers")
    st.caption(
        "Demo definition: 5 or fewer units in the selected period, no matching sale, "
        "or 30 or more days since the last matching sale. Recency is measured at the "
        "selected period end, not today's date. This does not measure inventory."
    )
    slow = performance.loc[performance["slow_mover"], ["product_name", "units", "last_sale", "days_since_sale"]]
    if slow.empty:
        st.info("No products meet the demo slow-mover definition in this selection.")
    else:
        st.dataframe(
            slow.rename(columns={"product_name": "Product", "units": "Units sold", "last_sale": "Last matching sale", "days_since_sale": "Days since sale"}),
            column_config={
                "Last matching sale": st.column_config.DateColumn(format="DD MMM YYYY"),
                "Days since sale": st.column_config.NumberColumn(format="%d"),
            },
            hide_index=True, width="stretch", alt="Products meeting the illustrative slow-mover definition.",
        )


render_products()
