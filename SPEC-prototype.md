# BAISKET clickable prototype

Approved scope: a Streamlit + Plotly walkthrough for the team and instructor,
not the working analytics system proposed in `BAisket.docx`.

## Screens and acceptance
- Sales Overview: sample revenue, distinct orders, average order value, and
  revenue trend. Date/category filters update sample metrics and charts.
- Product Analysis: revenue/units rankings, categories, slow movers, and
  selectable product details.
- Clustering: selectable illustrative K-means/DBSCAN scenarios, cluster
  profiles, and membership. No algorithm executes.
- Recommendations: fixed illustrative association rules with support,
  confidence, lift, filters, and bundle/cross-sell details. No Apriori executes.
- Data Upload: CSV picker displays filename/size and offers a sample-data
  walkthrough. Uploaded files are not parsed, cleaned, analyzed, or saved.

Every screen has working navigation and a visible demo notice. Cluster and
rule results are explicitly illustrative, not model-generated; sales filters
must not imply these fixed results were recomputed. Empty selections have
useful empty states. Charts and navigation must work on narrow screens.

## Stack and setup
Python 3.12, Streamlit, Plotly, Pandas, and pytest. Versions are pinned in
`requirements.txt` and `requirements-dev.txt`. From the root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m pytest -q
```

No separate build, lint, or typecheck command is configured for this milestone.

## Structure and style
`app.py` owns the common frame and native Streamlit navigation. Screen scripts
live in `src/views/`; `src/demo_data.py` owns the deterministic sample catalog
and transactions; `src/demo_logic.py` owns calculations and filters.
`tests/` contains pytest logic tests and Streamlit AppTest interaction tests.
Keep calculations out of screen rendering; use descriptive snake_case names.

```python
st.info("Illustrative demo results; no clustering algorithm is running.")
```

## Verification
Test sample totals, distinct-order counts, filters, rankings, empty selections,
and consistency of fixture references. Test navigation and screen interactions
with AppTest. Verify actual charts, keyboard controls, console output, and
desktop/narrow layouts in a browser. Review sales/product screens before the
remaining screens; review the complete walkthrough at the next checkpoint.

## Boundaries
- Always label demo results honestly and keep sample data deterministic.
- Ask before adding real CSV processing, algorithms, storage, authentication,
  or changing the agreed stack.
- Never claim model evaluation, save uploaded files, or add inventory/live-store
  features for this milestone.

Dataset selection, production CSV schema, cleaning policies, and formal
evaluation are deferred. The proposal document is unchanged.
