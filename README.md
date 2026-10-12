# BAISKET

A clickable sales-intelligence prototype for small online businesses.
The five-screen local walkthrough is complete and polished, not the full analytics
system proposed in `BAisket.docx`.
The original proposal document is kept locally and is not included in this repository.

## Get the project
This repository is public, so members can clone it without an invitation.
To let members push changes, the owner can invite them under
**Settings → Collaborators** on GitHub; members must accept the invitation.

```powershell
git clone https://github.com/bilangelg/BAISKET.git
cd BAISKET
```

## Try it locally
Requires Python 3.12. From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://127.0.0.1:8501. Stop the server with Ctrl+C in its terminal.
The server binds to localhost; it is not deployed or connected to a store.

## What works now
- Sales Overview: date/category filters, revenue, distinct order count, average
  order value, units sold, interactive revenue chart, and daily figures.
- Product Analysis: date/category filters, revenue/units rankings, selectable
  product details, category summaries, and slow-mover highlights.
- Clustering: illustrative K-means/DBSCAN scenario selection, cluster map,
  selected profiles, and member products.
- Recommendations: fixed rule examples, scope/support/confidence/lift filters,
  reset and empty states, and selected bundle/cross-sell details.
- Data Upload: CSV filename/size preview and a built-in sample walkthrough.
- Navigation across all five screens, with a persistent demo notice.

The deterministic fictional shop contains eight products and 120 orders from
July–September 2026. Display prices are in PHP. Sales totals are calculated
from those sample records, not hardcoded dashboard numbers.
Money displays use the peso symbol, grouping, and two decimals. Tables retain
numeric values for sorting; dates, percentages, and lift use readable display
formats consistent with the charts and detail panels.

With a category filter, average order value uses selected-category revenue
divided by matching orders, not entire-basket revenue. The demo slow-mover
flag means 5 or fewer units sold in the selection, no matching sale, or at
least 30 days since the last matching sale, measured at the selected period
end. It does not indicate stock or inventory levels.

## What is simulated
Cluster memberships are hand-assigned storyboards. Their numeric profiles use
the full sample period, regardless of filters on other pages. The 12 rule
examples have fixed metrics consistent with the sample baskets; they are not
mined or model-generated. Rule scopes reference the fixed K-means segments,
not the selected DBSCAN storyboard. A segment scope counts baskets containing
at least one member product. Both products in a rule belong to that segment.
Changing thresholds filters examples only; lift at or below 1 is always excluded.
Some scopes intentionally have no eligible examples.

Uploads are optional and capped at 5 MB in the picker. Choose dummy data only:
Streamlit temporarily holds the bytes in server memory. Application code reads
only filename and byte size, renders names as literal text, and never reads,
parses, saves, or analyzes contents. The sample-data button does not use the
selected file; it opens the prebuilt walkthrough. No CSV format validation occurs.

## Outside this milestone
No K-means, DBSCAN, Apriori, file processing, database, authentication, or
live-store integration is included in this milestone.

## Verify
```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q tests/test_app.py -k product
```

The verification suite has **62 passing tests** covering sample calculations and
Streamlit AppTest interactions, including
navigation, filtering, selection, empty states, fixture consistency, and heading
hierarchy. Upload tests forbid content-reading methods, including during the
sample walkthrough, and cover invalid/empty contents and untrusted filenames.
There is no separate build, lint, or typecheck command.

All five screens were checked at 320, 768, 1024, and 1440px widths
with no page-level horizontal overflow, clipped metric values, or uncaught
JavaScript errors.
Final checks also covered formatted chart tooltips, daily-table keyboard expansion,
and the sample walkthrough's keyboard-activated button and dashboard link.
Earlier Lighthouse accessibility scores: Sales Overview 91/100; Clustering 95/100.
Remaining audit warnings concern native Streamlit sidebar/date-input ARIA
and date-segment touch targets. This is not a claim of full WCAG compliance.
Direct child URLs can log two failed Streamlit base-path probes before falling
back to the root endpoints successfully. Open the root URL and use navigation.

## Suggested review walkthrough
1. Open Data Upload. Optionally choose a dummy CSV; confirm only name/size appear.
2. Click **Use built-in demo data** and follow the dashboard links.
3. Change sales/product dates and categories; inspect a product and its rankings.
4. On Clustering, switch scenarios and inspect a segment or the DBSCAN outliers.
5. On Recommendations, inspect a bundle/cross-sell rule, change thresholds or
   scope, then try an empty selection and **Reset filters**.

Both review checkpoints were approved, and final polish and verification are
complete. No production analytics or deployment is authorized by those reviews.

## Scope and progress
- Approved scope: [SPEC-prototype.md](SPEC-prototype.md)
- Implementation decisions: [tasks/plan.md](tasks/plan.md)
- Tasks and review gates: [tasks/todo.md](tasks/todo.md)

Framework references:
[native navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation),
[AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest),
[Plotly charts](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart),
[wrapping containers](https://docs.streamlit.io/develop/api-reference/layout/st.container),
[sliders](https://docs.streamlit.io/develop/api-reference/widgets/st.slider),
[file uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader),
[page links](https://docs.streamlit.io/develop/api-reference/widgets/st.page_link),
[numeric column formats](https://docs.streamlit.io/develop/api-reference/data/st.column_config/st.column_config.numbercolumn),
[date column formats](https://docs.streamlit.io/develop/api-reference/data/st.column_config/st.column_config.datecolumn),
[chart hover formats](https://plotly.com/python/hover-text-and-formatting/).
