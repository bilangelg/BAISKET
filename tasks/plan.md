# BAISKET prototype implementation plan

Scope and acceptance: `../SPEC-prototype.md`.
Tasks and current progress: `todo.md`. Approved in conversation.

## Decisions
- Use native Streamlit navigation, a shared demo notice, and a restrained
  green/light theme; use native widgets rather than custom HTML controls.
- Keep one deterministic sample catalog and transaction set. Use sample PHP
  prices for display; this does not constrain the future production currency.
- Keep calculations separate from rendering. Cluster/rule scenarios will be
  fixed fixtures clearly distinguished from real analytics.
- Rule scopes use the fixed K-means storyboard, with basket denominators based
  on orders containing at least one member product. Metrics remain fixed and
  are checked against the shared sample only for consistency, not model validity.
- The CSV picker caps files at 5 MB and previews metadata only. Streamlit holds
  bytes in memory; application code never reads or saves contents. The sample
  walkthrough is independent of file selection.
- Versions are verified against PyPI and pinned. Use installed Python 3.12,
  because the default `python` on this machine resolves to Python 3.9.
- Implement sequentially: screens share fixtures and rendering conventions.
- Leave changes uncommitted unless the user requests commits.

## Dependency order
Setup/navigation -> Sales Overview -> Product Analysis -> human review.
Then Clustering -> Recommendations -> Upload -> human review -> finish checks.
Each screen is a working vertical slice with tests, not a disconnected mockup.

## Final-polish design contract
- Preserve the approved navigation, green/light palette, spacing, and native
  controls. The approved walkthrough is the visual reference, not a new template.
- Keep each screen's action unchanged: filter sales, rank/inspect products,
  switch/inspect cluster storyboards, filter/inspect rules, or start the sample
  walkthrough from the metadata-only upload screen.
- Standardize money to PHP with grouping and two decimals; show readable dates,
  percentage suffixes, and lift multipliers. Format presentation only so table
  numbers remain numeric for sorting and totals.
- Retain demo notices, useful empty/partial selections, and upload success states.
  Keep heading levels, keyboard controls, and wrapping metric rows intact.
- Verify all five screens at 320/768/1024/1440px, including chart tooltips and
  lower-page tables/details. Table-local horizontal scrolling is acceptable;
  page overflow and clipped metric values are not.
- Reject a redesign, decorative gradients/cards, new dependencies, custom widget
  accessibility patches, and any analytics or upload-content processing.

## Risks and mitigation
- Demo inconsistencies: derive sales totals from one shared transaction set;
  validate that later cluster/rule fixtures reference the same products.
- Misleading simulations: keep persistent demo labels and explicit notices
  beside cluster/rule/upload actions.
- Framework/runtime mismatches: verify APIs in official documentation, then
  test with AppTest and a real browser.
- Mobile overflow: check 320, 768, 1024, and 1440px widths before each review.

## Verification sources
- https://docs.streamlit.io/develop/api-reference/navigation/st.navigation
- https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
- https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart

Dataset selection and real analytics are deliberately not implementation blockers.
