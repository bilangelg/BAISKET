import streamlit as st


st.set_page_config(page_title="BAISKET | Sales intelligence", page_icon="🧺", layout="wide")

# Keep long page titles readable at 320px without splitting a word in half.
# Static presentation only; no user input or JavaScript enters this HTML.
# https://docs.streamlit.io/develop/api-reference/text/st.html
st.html("<style>@media (max-width: 480px) { [data-testid='stMain'] h1 { font-size: 1.75rem; } }</style>")

st.sidebar.markdown("## BAISKET")
st.sidebar.caption("Sales intelligence for small businesses")
st.sidebar.divider()
st.sidebar.caption("LOCAL PROTOTYPE\n\nA sample shop, not a connected store.")

# Entrypoint-owned navigation keeps the demo frame visible on every screen.
# https://docs.streamlit.io/develop/api-reference/navigation/st.navigation
page = st.navigation(
    [
        st.Page("src/views/sales.py", title="Sales Overview", icon=":material/dashboard:", default=True),
        st.Page("src/views/products.py", title="Product Analysis", icon=":material/inventory_2:"),
        st.Page("src/views/clustering.py", title="Clustering", icon=":material/hub:"),
        st.Page("src/views/recommendations.py", title="Recommendations", icon=":material/shopping_basket:"),
        st.Page("src/views/upload.py", title="Data Upload", icon=":material/upload_file:"),
    ]
)

st.info("Demo data · Clickable prototype. No store is connected and no analytics models are running.")
page.run()
