import streamlit as st


st.title("Data Upload")
st.caption("Start the proposed data-to-insights workflow.")
st.warning(
    "Use a dummy CSV, not real customer data. Streamlit temporarily holds uploads in server memory. "
    "This page only reads filename and size; file contents are not read, parsed, analyzed, or saved."
)

st.header("File metadata preview")
# UploadedFile.name is untrusted: never use it as a path or Markdown/HTML.
# https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
uploaded = st.file_uploader(
    "Choose a demo CSV (metadata only)", type=["csv"], max_upload_size=5, key="demo_upload",
    help="Optional. Choose one dummy CSV of up to 5 MB. Selecting a file does not start analysis.",
)
if uploaded is None:
    st.info("No file selected. Choose a dummy CSV to preview its metadata, or continue with the built-in sample below.")
else:
    with st.container(border=True):
        st.text(f"Filename: {uploaded.name}")
        st.text(f"Size: {uploaded.size:,} bytes")
    st.caption("Metadata only — the file's format and contents have not been validated.")

st.header("Sample-data walkthrough")
st.write(
    "The full system would upload, clean, group products, and recommend bundles. "
    "Here those steps are simulated: the fictional shop and illustrative results are already prepared. "
    "You can explore them without selecting a file."
)
if st.button("Use built-in demo data", type="primary", key="start_demo"):
    st.session_state["demo_walkthrough_started"] = True

if st.session_state.get("demo_walkthrough_started", False):
    st.success("Demo walkthrough ready — using only built-in sample data.")
    st.caption("Any selected file was not used. No cleaning, clustering, or rule mining ran.")
    st.write(
        "1. **Preparation (simulated):** the bundled sample already contains 120 orders and eight products.\n"
        "2. **Explore sales:** change dates and categories on the sales and product screens.\n"
        "3. **Review illustrative results:** select cluster scenarios, rule filters, and recommendation details."
    )
    # Native links retain the entrypoint's shared demo frame.
    # https://docs.streamlit.io/develop/api-reference/widgets/st.page_link
    st.page_link("src/views/sales.py", label="View Sales Overview", icon=":material/dashboard:", width="stretch")
    st.page_link("src/views/products.py", label="View Product Analysis", icon=":material/inventory_2:", width="stretch")
    st.page_link("src/views/clustering.py", label="View Clustering", icon=":material/hub:", width="stretch")
    st.page_link("src/views/recommendations.py", label="View Recommendations", icon=":material/shopping_basket:", width="stretch")
