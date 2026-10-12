import streamlit as st

from src.demo_data import load_association_rules, load_products, load_rule_scopes
from src.demo_logic import filter_rules


def reset_rule_filters():
    st.session_state.update(rules_scope="All orders", rules_support=5, rules_confidence=50, rules_lift=1.0)


def render_recommendations():
    st.title("Recommendations")
    st.caption("Explore opportunities for bundles and cross-selling. Sample prices are in PHP.")
    st.info("Illustrative examples: curated rules with fixed metrics. Apriori is not running.")
    st.caption("Sales filters and DBSCAN selections on other pages do not recompute these examples.")
    scopes = load_rule_scopes()
    with st.container(border=True):
        scope = st.selectbox("Rule scope", list(scopes), key="rules_scope")
        # Sliders filter examples only, with visible labels and percentage units.
        # https://docs.streamlit.io/develop/api-reference/widgets/st.slider
        support_column, confidence_column, lift_column = st.columns(3)
        with support_column:
            support = st.slider("Minimum support (%)", 0, 100, 5, format="%d%%", key="rules_support")
        with confidence_column:
            confidence = st.slider("Minimum confidence (%)", 0, 100, 50, format="%d%%", key="rules_confidence")
        with lift_column:
            lift = st.slider("Minimum lift", 1.0, 8.0, 1.0, 0.1, key="rules_lift")
        st.button("Reset filters", key="reset_rules", on_click=reset_rule_filters)
    if scope == "All orders":
        st.caption(f"Scope: {scopes[scope]} full sample baskets from July–September 2026.")
    else:
        st.caption(
            f"Scope: {scopes[scope]} sample baskets containing at least one product from the "
            f"fixed K-means '{scope}' segment. Both products in each rule belong to that segment."
        )
    st.caption("Only examples with lift greater than 1 are shown, ordered by lift then confidence.")
    with st.expander("How to read these metrics"):
        st.write(
            "Support is the share of scope baskets containing both products. Confidence is the share "
            "of baskets with the 'If bought' product that also contain the suggested product. "
            "Lift compares that confidence with how often the suggested product appears in this scope. "
            "A lift above 1 indicates positive association, not causation or guaranteed sales."
        )
    matches = filter_rules(load_association_rules(), scope, support / 100, confidence / 100, lift)
    if matches.empty:
        st.info(
            "No illustrative rules match. Lower thresholds or choose another scope, or reset the filters. "
            "The curated examples for this scope may have no lift above 1; no new rules are generated."
        )
        return

    products = load_products().set_index("product_id")
    names = products["product_name"].to_dict()
    table = matches.assign(
        antecedent=matches["antecedent_id"].map(names), consequent=matches["consequent_id"].map(names),
        support=(matches["support"] * 100).round(1), confidence=(matches["confidence"] * 100).round(1),
        lift=matches["lift"].round(2),
    )
    st.header("Illustrative rules")
    st.caption(f"{len(matches)} example rules match these filters.")
    st.caption("On narrow screens, scroll the table sideways for all columns, or inspect a rule below for its full metrics.")
    st.dataframe(
        table[["rule_id", "antecedent", "consequent", "support", "confidence", "lift", "suggestion"]].rename(
            columns={"rule_id": "Rule ID", "antecedent": "If bought", "consequent": "Suggest",
                     "support": "Support (%)", "confidence": "Confidence (%)", "lift": "Lift", "suggestion": "Idea"}
        ),
        column_config={
            "Support (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Confidence (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Lift": st.column_config.NumberColumn(format="%.2f×"),
        },
        hide_index=True, width="stretch", alt="Fixed illustrative rules matching the selected scope and thresholds.",
    )
    st.header("Recommendation details")
    labels = {
        rule.rule_id: f"{rule.rule_id} · {names[rule.antecedent_id]} → {names[rule.consequent_id]}"
        for rule in matches.itertuples()
    }
    if st.session_state.get("rule_selection") not in labels:
        st.session_state["rule_selection"] = next(iter(labels))
    selected = st.selectbox("Inspect a rule", list(labels), format_func=labels.get, key="rule_selection")
    rule = matches.set_index("rule_id").loc[selected]
    with st.container(border=True):
        antecedent, consequent = names[rule["antecedent_id"]], names[rule["consequent_id"]]
        st.subheader(f"{antecedent} → {consequent}")
        with st.container(horizontal=True):
            for label, value in zip(
                ["Support", "Confidence", "Lift"],
                [f"{rule['support']:.1%}", f"{rule['confidence']:.1%}", f"{rule['lift']:.2f}×"],
            ):
                st.metric(label, value, width=180)
        if rule["suggestion"] == "Bundle":
            st.write(f"**Bundle idea:** present {antecedent} and {consequent} together as an optional two-product set.")
        else:
            st.write(f"**Cross-sell idea:** when {antecedent} is in the basket, offer {consequent} as an optional add-on.")
        price = products.loc[rule["antecedent_id"], "unit_price"] + products.loc[rule["consequent_id"], "unit_price"]
        st.caption(f"Sample combined unit prices: ₱{price:,.2f}. No discount or pricing decision is applied.")
        st.caption(
            "These are fictional examples for reviewing the workflow, not validated business recommendations. "
            "High lift on a tiny sample can be misleading; no demand, profit, or inventory forecast is made."
        )


render_recommendations()
