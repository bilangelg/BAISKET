# Prototype tasks

Commands below use `.\.venv\Scripts\python.exe` from the repository root.
No separate application build command exists.

- [x] 1. Setup and navigation (no dependencies)
  - Acceptance: pinned dependencies install on Python 3.12; app launches with
    five destinations and a persistent demo notice. Pending screens are
    honestly identified as awaiting the next increment.
  - Files: requirements files, `.gitignore`, `.streamlit/config.toml` (setup);
    `app.py`, `src/views/` screen scripts, `tests/test_app.py` (navigation).
    Add screen scripts in small tested increments rather than one large patch.
  - Verify: `-m pytest -q tests/test_app.py`; start with
    `-m streamlit run app.py` and inspect navigation in a browser.
- [x] 2. Sales Overview (depends on 1)
  - Acceptance: coherent sample metrics/trend; date/category filters work;
    empty results display a useful message.
  - Files: `src/demo_data.py`, `src/demo_logic.py`, `src/views/sales.py`,
    `tests/test_demo_logic.py`, `tests/test_app.py` (medium: 5 files).
  - Verify: `-m pytest -q`; exercise filters and chart in a browser.
- [x] 3. Product Analysis (depends on 2)
  - Acceptance: revenue/units rankings, category breakdown, explicit slow-mover
    definition, and product details respond to selection.
  - Files: `src/demo_logic.py`, `src/views/products.py`,
    `tests/test_demo_logic.py`, `tests/test_app.py` (medium: 4 files).
  - Verify: `-m pytest -q`; inspect sorting, details, and empty states.

## Checkpoint: sales/product review
- [x] Tests pass; browser console and desktop/narrow layout checks recorded.
- [x] README and AGENTS reflect executable setup and current limitations.
- [x] Human reviews the two working screens before the remaining features.
  Approved in conversation: "i reviewed the working pages and its fine."

- [x] 4. Clustering (depends on approved first checkpoint)
  - Acceptance: K-means/DBSCAN illustrative scenarios and cluster membership
    selection work; no computation is claimed.
  - Files: `src/demo_data.py`, `src/views/clustering.py`, fixture/UI tests
    (medium: up to 4 files).
  - Verify: `-m pytest -q`; switch scenarios and clusters in a browser.
- [x] 5. Recommendations (depends on 4)
  - Acceptance: fixed rule filters, support/confidence/lift display, and selected
    bundle/cross-sell details work with clear illustrative labels.
  - Files: `src/demo_data.py`, `src/demo_logic.py`,
    `src/views/recommendations.py`, logic/UI tests (medium: 5 files).
  - Verify: `-m pytest -q`; check filters and rule detail in a browser.
- [x] 6. Upload demonstration (depends on 5)
  - Acceptance: CSV metadata is visible; sample walkthrough works; no file
    parsing, saving, or analytics claims.
  - Files: `src/views/upload.py`, `tests/test_app.py` (small: 2 files).
  - Verify: `-m pytest -q`; select a dummy CSV in a browser and check notices.

## Checkpoint: full walkthrough review
- [x] Tests pass; all five screens and actions work in a browser.
- [x] Human reviews the complete prototype.
  Approved in conversation: "i like it ... do the final polishing."

- [x] 7. Finish checks and documentation (depends on second checkpoint)
  - Acceptance: startup instructions and AGENTS match actual commands; all
    acceptance checks are recorded with any limitations.
  - Files: `README.md`, `AGENTS.md`, `tasks/todo.md`; targeted UI fixes as needed.
  - Verify: run affected tests after fixes; check keyboard navigation and
    320/768/1024/1440px layouts; inspect browser errors and warnings.

## First-checkpoint verification (2026-10-13)
- `.\.venv\Scripts\python.exe -m pytest -q --tb=short`: 29 passed.
  Includes root-entrypoint navigation, sales/product filters, empty and partial
  date selections, ranking mode, product details, category totals, and headings.
- `.\.venv\Scripts\python.exe -m pip check`: no broken requirements.
- Real browser: navigation and ranking toggle work; category selection via
  keyboard changed Sales Overview to Stationery totals (PHP 16,950; 45 matching
  orders; 150 units). Browser console contains no warnings or errors.
- Isolated headless Edge: both screens checked at 320/768/1024/1440px; no
  page/main horizontal overflow or clipped metric text, charts stay inside the
  viewport, demo notice present, no uncaught JavaScript errors. Mobile/desktop
  screenshots reviewed. Fixed currency-value truncation using wrapping metrics.
- Sales Overview Lighthouse: accessibility 91/100 and best practices 100/100.
  Fixed caption contrast, heading levels, and invalid grouped-navigation lists.
  Remaining native Streamlit sidebar/date-input ARIA and date-segment touch
  targets are documented in README; full WCAG compliance is not claimed.
- Review mutation: replacing distinct-order counting with line counting in an
  isolated Python process made its regression test fail as expected. Repository
  source was never mutated by that experiment.
- Original `BAisket.docx` is unchanged. Files remain uncommitted; generated
  `.venv` and caches are ignored. At that checkpoint, tasks 4–6 waited for the
  human review now recorded as approved above.

## Full-walkthrough checkpoint verification (2026-10-13)
- `.\.venv\Scripts\python.exe -m pytest -q --tb=short`: **55 passed**.
  New coverage includes both cluster scenarios, member/profile selection,
  rule fixture consistency, inclusive thresholds with strict lift > 1,
  direction-sensitive details, scope changes, reset/empty states, and uploads.
- Upload tests forbid `read`, `readinto`, `readline`, `readlines`, `getvalue`, and
  `getbuffer` during application runs, including the sample action. Empty and
  invalid CSV contents still produce metadata only; Markdown/HTML-like names
  remain literal text. The sample sales total remains unchanged.
- Real browser: scenario/segment selection, rule selection, keyboard thresholds,
  and scoped denominators checked. A generated 68-byte dummy CSV showed only
  filename/size; removal restored the empty state. Native upload/delete requests
  returned 204. No application file-reading or file-writing path exists.
- Isolated Edge: all five screens checked at 320/768/1024/1440px. No page/main
  horizontal overflow, clipped metric values, or uncaught JavaScript errors;
  chart bounds and demo notices verified. Top/detail screenshots reviewed.
  Fixed the Recommendations title splitting mid-word on narrow screens.
- At 320 and 1440px, Enter activated the sample button without an upload and
  its native Sales Overview link opened the shared frame and sample dashboard.
- Clustering Lighthouse: accessibility 95/100, best practices 100/100. The native
  sidebar ARIA warning remains. Known native-widget accessibility limitations
  and direct-child-URL base-path probes are documented in README. Failed child
  probes fell back to root endpoints with 200 responses; a fresh root-entry
  browser session has a clean console.
- Review mutation: allowing lift == 1 in an isolated process failed the boundary
  regression test as expected. Repository source was not changed by this check.
- Reviewed correctness, readability, structure, input safety, and bounded sample
  work. No new dependencies, real analytics, storage, or external integration.
- README includes the complete review walkthrough; AGENTS and plan reflect the
  actual semantics. `BAisket.docx` remains untouched. Changes are uncommitted.
- The human review gate was subsequently approved; task 7 is complete below.
  Approval does not authorize production analytics or deployment.

## Final-polish verification (2026-10-13)
- Preserved the approved layout, navigation, green/light theme, and native
  controls. No new dependencies or demo-data/business-logic changes.
- Standardized table currency, dates, percentage suffixes, and lift multipliers;
  refined chart axes/tooltips and product recency copy. Values stay numeric for
  sorting and totals. Added a narrow-screen table hint to Product Analysis.
- New presentation regression tests were observed failing before implementation.
  Final `-m pytest -q --tb=short`: **62 passed**; `-m pip check`: no broken
  requirements. Upload-content guards and existing filters/empty states pass.
- Isolated Edge/CDP: all five screens at 320/768/1024/1440px have no page/main
  horizontal overflow, clipped metric values, or uncaught JavaScript errors.
  Desktop/narrow top and detail screenshots reviewed; tables scroll locally.
- Actual pointer hovers on all three charts at 320/1440px show full PHP values
  with two decimals; sales hovers show readable full dates, cluster hovers retain
  product and segment labels. Reviewed tooltip screenshots for clipping.
- Keyboard: Enter expands daily figures at 320/1440px; the sample button and
  Sales Overview link work without an upload. Arrow-key product ranking and
  keyboard DBSCAN selection work in the real browser.
- Fresh root-entry browser session has a clean console; health and host-config
  requests return 200 and the application WebSocket connects with 101. Known
  native-widget accessibility warnings and child-URL probes remain documented;
  full WCAG compliance is not claimed.
- Review mutation: inverting the new product ranking-format condition in memory
  fails the currency-hover regression assertion inside the shared demo frame.
  Repository source was not mutated by the experiment.
- Reviewed correctness, readability, structure, safety, and bounded sample work.
  README and AGENTS match current scope and commands. `BAisket.docx`, upload
  handling, fixtures, calculations, dependencies, and theme configuration are
  unchanged. At this checkpoint, changes were uncommitted as planned; nothing
  was deployed. The user subsequently authorized GitHub sharing, excluding the
  original proposal document.
