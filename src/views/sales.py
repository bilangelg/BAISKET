import plotly.express as px
import streamlit as st

from src.demo_data import load_sales
from src.demo_logic import filter_sales, revenue_trend, sales_summary


def render_sales():
    sales = load_sales()
    st.title("Sales Overview")
    st.caption("A clear picture of how your sample shop is performing. Sample prices are in PHP.")

    with st.container(border=True):
        period_column, category_column = st.columns([2, 1])
        with period_column:
            dates = st.date_input(
                "Sales period",
                value=(sales["sales_date"].min().date(), sales["sales_date"].max().date()),
                key="sales_dates",
                format="DD/MM/YYYY",
            )
        with category_column:
            category = st.selectbox(
                "Product category",
                ["All categories", *sorted(sales["category"].unique())],
                key="sales_category",
            )

    if len(dates) != 2:
        st.info("Choose an end date to complete your sales period.")
        return
    filtered = filter_sales(sales, dates[0], dates[1], category)
    summary = sales_summary(filtered)
    # Wrapping cards keep the full value visible instead of ellipsizing narrow columns.
    with st.container(horizontal=True):
        for label, value in zip(
            ["Revenue", "Orders", "Average order value", "Units sold"],
            [
                f"₱{summary['revenue']:,.2f}",
                f"{summary['orders']:,}",
                f"₱{summary['average_order_value']:,.2f}",
                f"{summary['units']:,}",
            ],
        ):
            st.metric(label, value, border=True, width=220)
    st.caption(
        "Metrics use matching orders and product lines only. With a category filter, "
        "average order value means selected-category revenue divided by matching orders, "
        "not the value of the entire basket."
    )
    if filtered.empty:
        st.info("No sales match these filters. Try another period or category.")
        return

    st.header("Revenue over time")
    trend = revenue_trend(filtered)
    chart = px.line(
        trend,
        x="sales_date",
        y="revenue",
        labels={"sales_date": "Date", "revenue": "Revenue (PHP)"},
        color_discrete_sequence=[st.get_option("theme.primaryColor")],
    )
    # https://plotly.com/python/hover-text-and-formatting/
    chart.update_traces(
        fill="tozeroy", fillcolor="rgba(22,100,81,0.08)",
        hovertemplate="Revenue: ₱%{y:,.2f}<extra></extra>",
    )
    chart.update_layout(margin=dict(l=0, r=0, t=16, b=0), height=340, hovermode="x unified")
    chart.update_xaxes(hoverformat="%d %b %Y")
    chart.update_yaxes(rangemode="tozero", tickformat=",.0f")
    # Use width and alt rather than the deprecated use_container_width parameter.
    # https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
    st.plotly_chart(
        chart,
        width="stretch",
        config={"displaylogo": False, "scrollZoom": False},
        alt="Daily sample-shop revenue in PHP for the selected period and category.",
    )
    peak = trend.loc[trend["revenue"].idxmax()]
    st.caption(f"Peak day: {peak['sales_date']:%d %b %Y} · ₱{peak['revenue']:,.2f}")
    with st.expander("View the daily figures"):
        # Column formatting preserves numeric values and chronological sorting.
        # https://docs.streamlit.io/develop/api-reference/data/st.column_config
        st.dataframe(
            trend.rename(columns={"sales_date": "Date", "revenue": "Revenue (PHP)"}),
            column_config={
                "Date": st.column_config.DateColumn(format="DD MMM YYYY"),
                "Revenue (PHP)": st.column_config.NumberColumn(format="₱%,.2f"),
            },
            hide_index=True,
            width="stretch",
            alt="Daily revenue figures underlying the chart.",
        )


render_sales()
