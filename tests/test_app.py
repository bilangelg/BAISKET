import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_opens_with_sales_overview_and_demo_notice():
    app = AppTest.from_file(APP, default_timeout=10).run()

    assert not app.exception
    assert app.title[0].value == "Sales Overview"
    assert any("Demo data" in notice.value for notice in app.info)


@pytest.mark.parametrize(
    ("page", "title"),
    [
        ("sales", "Sales Overview"),
        ("products", "Product Analysis"),
        ("clustering", "Product Clustering"),
        ("recommendations", "Recommendations"),
        ("upload", "Data Upload"),
    ],
)
def test_navigation_opens_each_screen_with_demo_notice(page, title):
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page(f"src/views/{page}.py").run()

    assert not app.exception
    assert app.title[0].value == title
    assert any("Demo data" in notice.value for notice in app.info)


def test_sales_category_filter_changes_metrics():
    app = AppTest.from_file(APP, default_timeout=10).run()
    all_revenue = app.metric[0].value
    app.selectbox(key="sales_category").select("Stationery").run()

    assert not app.exception
    assert app.metric[0].value != all_revenue
    assert any("matching orders" in caption.value for caption in app.caption)


def test_sales_date_filter_handles_no_matches():
    from datetime import date

    app = AppTest.from_file(APP, default_timeout=10).run()
    app.date_input(key="sales_dates").set_value((date(2027, 1, 1), date(2027, 1, 2))).run()

    assert not app.exception
    assert any("No sales match" in notice.value for notice in app.info)


def test_sales_partial_date_range_has_a_useful_message():
    from datetime import date

    app = AppTest.from_file(APP, default_timeout=10).run()
    app.date_input(key="sales_dates").set_value((date(2026, 7, 1),)).run()

    assert not app.exception
    assert any("end date" in notice.value for notice in app.info)


def test_sales_daily_table_formats_money_and_dates_without_stringifying_values():
    app = AppTest.from_file(APP, default_timeout=10).run()
    table = app.dataframe[0]
    columns = json.loads(table.proto.columns)

    assert not app.exception
    assert columns["Revenue (PHP)"]["type_config"]["format"] == "₱%,.2f"
    assert columns["Date"]["type_config"]["format"] == "DD MMM YYYY"
    assert table.value["Revenue (PHP)"].dtype.kind in "if"
    assert table.value["Revenue (PHP)"].sum() == 98_306


def test_sales_chart_has_readable_date_and_currency_hover_labels():
    app = AppTest.from_file(APP, default_timeout=10).run()
    chart = json.loads(app.get("plotly_chart")[0].proto.spec)

    assert "₱%{y:,.2f}" in chart["data"][0]["hovertemplate"]
    assert chart["layout"]["xaxis"]["hoverformat"] == "%d %b %Y"


def test_product_ranking_switch_updates_table():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.radio(key="product_ranking").set_value("Units sold").run()

    assert not app.exception
    table = app.dataframe[0].value
    assert table["Units sold"].tolist() == sorted(table["Units sold"], reverse=True)
    app.radio(key="product_ranking").set_value("Revenue").run()
    table = app.dataframe[0].value
    assert table["Revenue (PHP)"].tolist() == sorted(table["Revenue (PHP)"], reverse=True)


def test_product_tables_format_money_and_recency_without_changing_numeric_totals():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()

    assert not app.exception
    for table in app.dataframe[:2]:
        columns = json.loads(table.proto.columns)
        assert columns["Revenue (PHP)"]["type_config"]["format"] == "₱%,.2f"
        assert table.value["Revenue (PHP)"].dtype.kind in "if"
        assert table.value["Revenue (PHP)"].sum() == 98_306
    slow_columns = json.loads(app.dataframe[2].proto.columns)
    assert slow_columns["Last matching sale"]["type_config"]["format"] == "DD MMM YYYY"
    assert slow_columns["Days since sale"]["type_config"]["format"] == "%d"


@pytest.mark.parametrize(
    ("ranking", "hover_value"), [("Revenue", "₱%{x:,.2f}"), ("Units sold", "%{x:,d}")]
)
def test_product_chart_formats_hover_values_for_the_selected_ranking(ranking, hover_value):
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.radio(key="product_ranking").set_value(ranking).run()

    assert not app.exception
    chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    assert hover_value in chart["data"][0]["hovertemplate"]


def test_product_selection_updates_details():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.selectbox(key="product_detail").set_value("P008").run()

    assert not app.exception
    assert any(heading.value == "Desk Organizer" for heading in app.subheader)
    assert any("Slow mover" in notice.value for notice in app.warning)


def test_product_category_filter_limits_rankings_and_detail_options():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.selectbox(key="products_category").set_value("Stationery").run()

    assert not app.exception
    assert set(app.dataframe[0].value["Product"]) == {"Desk Notebook", "Gel Pen Set"}
    assert set(app.selectbox(key="product_detail").options) == {"Desk Notebook", "Gel Pen Set"}


def test_products_no_matching_sales_have_empty_state():
    from datetime import date

    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.date_input(key="products_dates").set_value((date(2027, 1, 1), date(2027, 1, 2))).run()

    assert not app.exception
    assert any("No sales match" in notice.value for notice in app.info)


def test_products_partial_date_range_has_a_useful_message():
    from datetime import date

    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()
    app.date_input(key="products_dates").set_value((date(2026, 7, 1),)).run()

    assert not app.exception
    assert any("end date" in notice.value for notice in app.info)


def test_category_breakdown_totals_match_rankings():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()

    rankings = app.dataframe[0].value
    categories = app.dataframe[1].value
    assert categories["Revenue (PHP)"].sum() == rankings["Revenue (PHP)"].sum()
    assert categories["Units sold"].sum() == rankings["Units sold"].sum()


def test_slow_movers_are_visible_with_an_explicit_demo_definition():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()

    assert set(app.dataframe[2].value["Product"]) == {"Scented Candle", "Desk Organizer"}
    assert any("5 or fewer" in caption.value and "30" in caption.value for caption in app.caption)


def test_sales_sections_do_not_skip_heading_levels():
    app = AppTest.from_file(APP, default_timeout=10).run()

    assert "Revenue over time" in [heading.value for heading in app.header]


def test_product_sections_use_second_level_headings():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/products.py").run()

    assert {heading.value for heading in app.header} == {
        "Product rankings", "Product details", "Category performance", "Slow movers"
    }


def test_cluster_selection_updates_profile_and_members():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/clustering.py").run()
    app.selectbox(key="cluster_selection").set_value("Slow movers").run()

    assert not app.exception
    assert set(app.dataframe[0].value["Product"]) == {"Scented Candle", "Desk Organizer"}
    assert app.metric[0].value == "2"
    assert any("Illustrative" in notice.value and "not running" in notice.value for notice in app.info)


def test_algorithm_selection_changes_the_illustrative_scenario():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/clustering.py").run()
    app.selectbox(key="cluster_algorithm").set_value("DBSCAN").run()
    app.selectbox(key="cluster_selection").set_value("Outliers").run()

    assert not app.exception
    assert set(app.dataframe[0].value["Product"]) == {"Scented Candle", "Desk Organizer"}
    assert any("not a measured anomaly" in caption.value for caption in app.caption)


def test_cluster_chart_and_member_table_format_values_without_losing_segment_labels():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/clustering.py").run()

    assert not app.exception
    columns = json.loads(app.dataframe[0].proto.columns)
    assert columns["Revenue (PHP)"]["type_config"]["format"] == "₱%,.2f"
    assert app.dataframe[0].value["Revenue (PHP)"].dtype.kind in "if"
    chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    for trace in chart["data"]:
        assert "₱%{y:,.2f}" in trace["hovertemplate"]
        assert "%{x:,d}" in trace["hovertemplate"]
        assert "Demo segment: %{customdata[0]}" in trace["hovertemplate"]
        assert all(row[0] == trace["name"] for row in trace["customdata"])


def test_recommendations_show_directional_rules_and_illustrative_notice():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()

    assert not app.exception
    table = app.dataframe[0].value
    assert set(table["Rule ID"]) == {"R001", "R002", "R003", "R004", "R005"}
    assert (table["Lift"] > 1).all()
    assert {"If bought", "Suggest", "Support (%)", "Confidence (%)"} <= set(table.columns)
    assert any("Illustrative" in notice.value and "Apriori is not running" in notice.value for notice in app.info)


def test_rule_table_formats_percentages_and_lift_without_stringifying_values():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    table = app.dataframe[0]
    columns = json.loads(table.proto.columns)

    assert not app.exception
    for name in ["Support (%)", "Confidence (%)"]:
        assert columns[name]["type_config"]["format"] == "%.1f%%"
        assert table.value[name].dtype.kind in "if"
    assert columns["Lift"]["type_config"]["format"] == "%.2f×"
    assert table.value["Lift"].dtype.kind in "if"
    assert table.value.set_index("Rule ID").loc["R001", "Support (%)"] == 25.0


def test_rule_selection_updates_bundle_details_and_metrics():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.selectbox(key="rule_selection").set_value("R001").run()

    assert not app.exception
    assert any("Desk Notebook → Gel Pen Set" == heading.value for heading in app.subheader)
    assert [metric.value for metric in app.metric] == ["25.0%", "66.7%", "2.67×"]
    assert any("Bundle idea" in message.value for message in app.markdown)
    assert any("₱218.00" in caption.value for caption in app.caption)


def test_rule_selection_updates_cross_sell_direction():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.selectbox(key="rule_selection").set_value("R005").run()

    assert not app.exception
    assert any(heading.value == "Bamboo Coaster → Coffee Beans" for heading in app.subheader)
    assert any("Cross-sell idea" in message.value for message in app.markdown)
    assert [metric.value for metric in app.metric] == ["12.5%", "50.0%", "1.33×"]


def test_rule_filters_only_show_examples_matching_the_thresholds():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.slider(key="rules_support").set_value(25).run()
    app.slider(key="rules_confidence").set_value(100).run()
    app.slider(key="rules_lift").set_value(2.0).run()

    assert not app.exception
    table = app.dataframe[0].value
    assert set(table["Rule ID"]) == {"R002", "R004"}
    assert (table["Support (%)"] >= 25).all()
    assert (table["Confidence (%)"] >= 100).all()
    assert (table["Lift"] >= 2.0).all()


def test_rule_scope_changes_examples_and_explains_basket_denominator():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.selectbox(key="rules_scope").set_value("Steady performers").run()

    assert not app.exception
    assert set(app.dataframe[0].value["Rule ID"]) == {"R009", "R010"}
    assert any("75" in caption.value and "at least one" in caption.value for caption in app.caption)
    assert any("K-means" in caption.value for caption in app.caption)


def test_unmatched_rule_filters_have_empty_state_and_can_be_reset():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.slider(key="rules_support").set_value(100).run()

    assert not app.exception
    assert any("No illustrative rules match" in notice.value for notice in app.info)
    assert not app.dataframe
    assert not app.selectbox(key="rules_scope").disabled
    app.button(key="reset_rules").click().run()
    assert not app.exception
    assert app.slider(key="rules_support").value == 5
    assert len(app.dataframe[0].value) == 5


def test_upload_starts_with_metadata_only_notice_and_optional_sample_action():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/upload.py").run()

    assert not app.exception
    assert any("No file selected" in notice.value for notice in app.info)
    assert any("memory" in notice.value and "dummy CSV" in notice.value for notice in app.warning)
    assert app.file_uploader(key="demo_upload").proto.max_upload_size_mb == 5
    assert not app.button(key="start_demo").disabled


@pytest.mark.parametrize("contents", [b"", b"this is deliberately not a valid CSV\x00\xff"])
def test_upload_shows_only_filename_and_byte_size_then_clears(contents):
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/upload.py").run()
    app.file_uploader(key="demo_upload").set_value(("dummy.csv", contents, "text/csv")).run()

    assert not app.exception
    assert app.text[0].value == "Filename: dummy.csv"
    assert app.text[1].value == f"Size: {len(contents)} bytes"
    assert not app.dataframe
    app.file_uploader(key="demo_upload").set_value(None).run()
    assert not app.exception
    assert not app.text
    assert any("No file selected" in notice.value for notice in app.info)


def test_upload_does_not_read_contents_even_when_starting_sample_walkthrough(monkeypatch):
    from streamlit.runtime.uploaded_file_manager import UploadedFile

    def reject_content_read(*args, **kwargs):
        raise AssertionError("The prototype must never read uploaded file contents.")

    for method in ["read", "readinto", "readline", "readlines", "getvalue", "getbuffer"]:
        monkeypatch.setattr(UploadedFile, method, reject_content_read)
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/upload.py").run()
    payload = ("invalid.csv", b"\xff\x00not csv", "text/csv")
    app.file_uploader(key="demo_upload").set_value(payload).run()
    # Explicit bytes avoid AppTest's own getvalue() call when it re-registers
    # an existing upload. The guard stays active throughout application runs.
    app.file_uploader(key="demo_upload").set_value(payload)
    app.button(key="start_demo").click().run()

    assert not app.exception
    assert any("built-in sample data" in notice.value for notice in app.success)
    assert any("not used" in caption.value for caption in app.caption)
    assert len(app.get("page_link")) == 4
    app.file_uploader(key="demo_upload").set_value(None)
    app.switch_page("src/views/sales.py").run()
    assert not app.exception
    assert app.metric[0].value == "₱98,306.00"


def test_sample_walkthrough_can_start_without_uploading_a_file():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/upload.py").run()
    app.button(key="start_demo").click().run()

    assert not app.exception
    assert any("built-in sample data" in notice.value for notice in app.success)
    assert len(app.get("page_link")) == 4


@pytest.mark.parametrize("filename", ["![not-an-image](example).csv", "<img src=x onerror=alert(1)>.csv"])
def test_uploaded_filename_is_rendered_as_literal_text_not_markdown(filename):
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/upload.py").run()
    app.file_uploader(key="demo_upload").set_value((filename, b"dummy", "text/csv")).run()

    assert not app.exception
    assert app.text[0].value == f"Filename: {filename}"
    assert not app.get("imgs")
    assert not any(filename in message.value for message in app.markdown)


@pytest.mark.parametrize("scope", ["Top sellers", "Slow movers"])
def test_rule_scopes_without_positive_examples_explain_the_empty_state(scope):
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.selectbox(key="rules_scope").set_value(scope).run()
    app.slider(key="rules_support").set_value(0).run()
    app.slider(key="rules_confidence").set_value(0).run()

    assert not app.exception
    assert any("no lift above 1" in notice.value for notice in app.info)
    assert not app.dataframe


def test_rule_selection_is_valid_after_scope_changes_and_reset():
    app = AppTest.from_file(APP, default_timeout=10).run()
    app.switch_page("src/views/recommendations.py").run()
    app.selectbox(key="rule_selection").set_value("R005").run()
    app.selectbox(key="rules_scope").set_value("Steady performers").run()

    assert not app.exception
    assert app.selectbox(key="rule_selection").value in {"R009", "R010"}
    app.button(key="reset_rules").click().run()
    assert not app.exception
    assert app.selectbox(key="rules_scope").value == "All orders"
    assert app.selectbox(key="rule_selection").value in set(app.dataframe[0].value["Rule ID"])
