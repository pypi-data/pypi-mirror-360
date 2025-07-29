import math
import pytest

from dtree import DecisionTree


def build_simple_stock_tree():
    """Utility helper that builds the first example decision tree (Tesla stock buy)."""
    dt = DecisionTree()
    # Nodes
    dt.add_decision_node("D", "Decision")
    dt.add_chance_node("B", "Buy TSLA stocks")
    dt.add_terminal_node("NB", "Don't buy TSLA stocks", 0)
    dt.add_edge("D", "B")
    dt.add_edge("D", "NB")

    dt.add_terminal_node("PI", "The price increases", 1_000)
    dt.add_terminal_node("PD", "The price decreases", -2_000)
    dt.add_edge("B", "PI", 0.6)
    dt.add_edge("B", "PD", 0.4)
    return dt


def build_land_investment_tree(utility_function=None):
    """Utility helper that builds the land-investment tree from the notebook."""
    dt = DecisionTree(utility_function=utility_function)

    # Top level
    dt.add_decision_node("I", "Decision")
    dt.add_terminal_node("S", "Sell land", 22_000)
    dt.add_chance_node("D", "Drill land")
    dt.add_edge("I", "S")
    dt.add_edge("I", "D")

    # Drill outcome
    dt.add_decision_node("G", "Gas found")
    dt.add_terminal_node("NG", "No gas found", -40_000)
    dt.add_edge("D", "G", 0.3)
    dt.add_edge("D", "NG", 0.7)

    # If gas is found
    dt.add_terminal_node("GS", "Sell land to West Gas", 200_000 - 40_000)
    dt.add_chance_node("GD", "Develop the site")
    dt.add_edge("G", "GD")
    dt.add_edge("G", "GS")

    dt.add_terminal_node("NM", "Normal market conditions", 150_000 - 40_000)
    dt.add_terminal_node("GM", "Good market conditions", 300_000 - 40_000)
    dt.add_edge("GD", "NM", 0.4)
    dt.add_edge("GD", "GM", 0.6)

    return dt


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_simple_tree_expected_values():
    dt = build_simple_stock_tree()
    ev = dt.calculate_expected_values()

    # Expected values derived manually
    expected_values = {
        "PI": 1_000,
        "PD": -2_000,
        "B": -200.0,  # 0.6 * 1000 + 0.4 * -2000
        "NB": 0.0,
        "D": 0.0,  # max(0, -200)
    }

    # Assert expected values match (DecisionTree returns float for no utility function)
    for node_id, expected in expected_values.items():
        assert math.isclose(ev[node_id], expected, abs_tol=1e-6), f"{node_id} expected {expected}, got {ev[node_id]}"


def test_simple_tree_optimal_path():
    dt = build_simple_stock_tree()
    optimal_path = dt.get_optimal_path("D")
    assert optimal_path == ["D", "NB"], "Optimal path should choose not to buy TSLA stock"


def test_land_investment_expected_values():
    dt = build_land_investment_tree()
    ev = dt.calculate_expected_values()

    # Expected values computed manually (see example notebook)
    expected = {
        "I": 32_000.0,
        "S": 22_000.0,
        "D": 32_000.0,
        "G": 200_000.0,
        "NG": -40_000.0,
        "GS": 160_000.0,
        "GD": 200_000.0,
        "NM": 110_000.0,
        "GM": 260_000.0,
    }

    for node_id, exp_val in expected.items():
        assert math.isclose(
            ev[node_id], exp_val, abs_tol=1e-6
        ), f"{node_id} expected {exp_val}, got {ev[node_id]}"


def test_land_investment_with_utility_function():
    import numpy as np

    def utility(x):
        return np.cbrt(x).item()

    dt = build_land_investment_tree(utility_function=utility)
    ev = dt.calculate_expected_values()

    # The notebook reports the following values for node 'I'
    assert math.isclose(
        ev["I"]["expected_value"], 32_000.0, abs_tol=1e-6
    )
    assert math.isclose(
        ev["I"]["utility_value"], 31.74802103936399, rel_tol=1e-6
    ) 