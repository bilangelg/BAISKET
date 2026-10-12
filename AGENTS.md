# BAISKET context

- Current deliverable is the clickable prototype in `SPEC-prototype.md`, not the full analytics system in `BAisket.docx`. Both human review gates in `tasks/todo.md` were approved; all five screens, final polish, and verification are complete. Production analytics and deployment remain out of scope.
- The shared repository is `https://github.com/bilangelg/BAISKET.git`; public visibility was explicitly approved. Keep `BAisket.docx` local and ignored, as the user requested; do not stage it or force-add ignored files.

## Commands (PowerShell, repository root)
- Create the environment with `py -3.12 -m venv .venv`; this machine's default `python` resolves to Python 3.9, which cannot run the pinned stack.
- Install: `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` (includes runtime dependencies).
- Run: `.\.venv\Scripts\python.exe -m streamlit run app.py`; `.streamlit/config.toml` binds the server to localhost and disables usage telemetry.
- Verify: `.\.venv\Scripts\python.exe -m pytest -q`; focused UI checks: `.\.venv\Scripts\python.exe -m pytest -q tests/test_app.py -k product`.
- No separate build, lint, formatter, or typecheck command is configured.

## Wiring and demo semantics
- `app.py` owns native `st.navigation` and the persistent demo frame; screen scripts in `src/views/` execute through that entrypoint. Initialize AppTest from root `app.py`, run once, then use `switch_page("src/views/products.py").run()`; testing a child directly omits the common frame.
- `src/demo_data.py` supplies a fresh deterministic catalog/transaction set; `src/demo_logic.py` owns summaries and filters. Demo prices are PHP, not a production currency decision.
- Count orders with distinct transaction IDs, not line count. Category-filtered average order value uses only matching product revenue; preserve the UI explanation.
- Slow-mover recency is measured at the selected period end, never the current date. Its thresholds are illustrative and do not indicate inventory.
- Keep money metrics in wrapping `st.container(horizontal=True)` rows; equal-width columns clipped currency values even at desktop sizes. Check the inner metric text for ellipsis, not just page overflow.
- Use `st.column_config` for table money/date/percentage/lift presentation; retain numeric values for sorting and totals. Rule table percentages are already scaled to percentage points, so use `%.1f%%`, not a format that multiplies by 100 again.
- Cluster/rule fixtures reference the shared catalog and are explicitly illustrative. Memberships and rule metrics never recompute from sales filters or uploads. Rule scopes use the fixed K-means segments; scoped baskets contain at least one member product. Only lift > 1 is eligible, in addition to inclusive UI thresholds.
- Upload is metadata-only: use `UploadedFile.name` and `.size`, render filenames with `st.text`, and never read contents or use filenames as paths. The sample walkthrough uses built-in data regardless of upload. Its sole application session flag is `demo_walkthrough_started`.
- AppTest re-registers an existing upload with `getvalue()` between runs. Tests that forbid content reads must supply explicit fixture bytes via `set_value()` on each rerun; never relax the guard around application code.
- `server.runOnSave` is enabled for local development. A stale imported module during an older server session may require a rerun/restart, not application-side reload hacks. Direct child URLs can produce failed base-path probes before root fallback; use the root URL and native navigation for clean-console checks.
- Native grouped navigation caused invalid list markup in the verified Streamlit version; keep the ungrouped page list. Use `st.header` (h2) for sections following `st.title` (h1); `st.subheader` (h3) is for nested content. Remaining native-widget accessibility warnings are recorded in `README.md`.
