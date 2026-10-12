import plotly.express as px
import streamlit as st

from src.demo_data import load_cluster_membership, load_products, load_sales
from src.demo_logic import product_performance


st.title("Product Clustering")
st.caption("Explore products with similar sales behavior. Sample prices are in PHP.")
st.info("Illustrative scenario: labels are hand-assigned. K-means and DBSCAN are not running.")

with st.container(border=True):
    algorithm = st.selectbox("Demo algorithm", ["K-means", "DBSCAN"], key="cluster_algorithm")
    st.caption("Switching algorithms selects a different storyboard, not a newly trained model.")

sales = load_sales()
membership = load_cluster_membership(algorithm)
performance = product_performance(sales, load_products(), sales["sales_date"].max().date()).merge(
    membership, on="product_id", validate="one_to_one"
)
st.caption(
    "Numeric profiles summarize the full July–September 2026 sample sales. "
    "Filters on other pages do not change these fixed demo memberships."
)

st.header("Cluster map")
# Color and symbol both convey membership; labels are also available in the table.
# https://plotly.com/python-api-reference/generated/plotly.express.scatter.html
chart = px.scatter(
    performance,
    x="units", y="revenue", color="cluster", symbol="cluster",
    hover_name="product_name", custom_data=["cluster"],
    labels={"units": "Units sold", "revenue": "Revenue (PHP)", "cluster": "Demo segment"},
    color_discrete_sequence=[st.get_option("theme.primaryColor"), "#326E90", "#94592B"],
    render_mode="svg",
)
chart.update_traces(
    marker=dict(size=13),
    hovertemplate=(
        "<b>%{hovertext}</b><br>Demo segment: %{customdata[0]}"
        "<br>Units sold: %{x:,d}<br>Revenue: ₱%{y:,.2f}<extra></extra>"
    ),
)
chart.update_xaxes(tickformat=",d")
chart.update_yaxes(tickformat=",.0f")
chart.update_layout(
    height=380, margin=dict(l=0, r=0, t=16, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(
    chart, width="stretch", config={"displaylogo": False, "scrollZoom": False},
    alt="Sample product units and revenue, with illustrative segment membership shown by color and symbol.",
)

st.header("Cluster profile")
selected = st.selectbox("Inspect a segment", membership["cluster"].unique(), key="cluster_selection")
members = performance.loc[performance["cluster"].eq(selected)]
with st.container(horizontal=True):
    for label, value in zip(
        ["Products", "Avg units / product", "Avg revenue / product"],
        [str(len(members)), f"{members['units'].mean():.1f}", f"₱{members['revenue'].mean():,.2f}"],
    ):
        st.metric(label, value, border=True, width=220)
if selected == "Outliers":
    st.caption("Outliers is a storyboard label, not a measured anomaly or model evaluation result.")

st.header("Member products")
st.caption("On narrow screens, scroll the table sideways to see all columns.")
st.dataframe(
    members[["product_name", "category", "units", "revenue"]].rename(
        columns={"product_name": "Product", "category": "Category", "units": "Units sold", "revenue": "Revenue (PHP)"}
    ),
    column_config={"Revenue (PHP)": st.column_config.NumberColumn(format="₱%,.2f")},
    hide_index=True, width="stretch", alt=f"Sample products assigned to the illustrative {selected} segment.",
)
with st.expander("What would the full system do?"):
    st.write(
        "K-means would group scaled product-performance features. DBSCAN would "
        "compare density-based groups and identify possible noise points. "
        "Model fitting, cluster validity scores, and automatic labels are deferred."
    )
