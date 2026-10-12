import pandas as pd
import pytest

from src.demo_data import (
    load_association_rules, load_cluster_membership, load_products, load_rule_scopes, load_sales,
)


@pytest.mark.parametrize("algorithm", ["K-means", "DBSCAN"])
def test_cluster_examples_assign_every_catalog_product_once(algorithm):
    membership = load_cluster_membership(algorithm)

    assert membership["product_id"].is_unique
    assert set(membership["product_id"]) == set(load_products()["product_id"])
    assert membership["cluster"].notna().all()
    pd.testing.assert_frame_equal(membership, load_cluster_membership(algorithm))


def test_dbscan_example_identifies_outliers_without_running_a_model():
    membership = load_cluster_membership("DBSCAN")

    assert set(membership.loc[membership["cluster"].eq("Outliers"), "product_id"]) == {"P006", "P008"}
    assert "Outliers" not in set(load_cluster_membership("K-means")["cluster"])


def test_rule_examples_reference_the_catalog_and_valid_metrics():
    rules = load_association_rules()
    ids = set(load_products()["product_id"])

    assert rules["rule_id"].is_unique
    assert set(rules["antecedent_id"]) <= ids
    assert set(rules["consequent_id"]) <= ids
    assert (rules["antecedent_id"] != rules["consequent_id"]).all()
    assert rules["support"].between(0, 1, inclusive="right").all()
    assert rules["confidence"].between(0, 1, inclusive="right").all()
    assert rules["lift"].gt(0).all()
    assert set(rules["scope"]) == set(load_rule_scopes())


def test_fixed_rule_metrics_are_consistent_with_sample_baskets():
    baskets = load_sales().groupby("transaction_id")["product_id"].agg(set).tolist()
    membership = load_cluster_membership()
    scopes = load_rule_scopes()

    for rule in load_association_rules().itertuples():
        scoped = baskets
        if rule.scope != "All orders":
            ids = set(membership.loc[membership["cluster"].eq(rule.scope), "product_id"])
            assert {rule.antecedent_id, rule.consequent_id} <= ids
            scoped = [basket & ids for basket in baskets if basket & ids]
        assert len(scoped) == scopes[rule.scope]
        antecedent_count = sum(rule.antecedent_id in basket for basket in scoped)
        consequent_count = sum(rule.consequent_id in basket for basket in scoped)
        joint_count = sum({rule.antecedent_id, rule.consequent_id} <= basket for basket in scoped)

        assert rule.support == pytest.approx(joint_count / len(scoped))
        assert rule.confidence == pytest.approx(joint_count / antecedent_count)
        assert rule.lift == pytest.approx(rule.confidence / (consequent_count / len(scoped)))


def test_rules_and_scopes_are_fresh_deterministic_fixtures():
    rules = load_association_rules()
    rules.loc[0, "support"] = 0
    scopes = load_rule_scopes()
    scopes["All orders"] = 0

    assert load_association_rules().loc[0, "support"] > 0
    assert load_rule_scopes()["All orders"] == 120
