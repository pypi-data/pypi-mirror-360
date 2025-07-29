import math
import numpy as np
import pytest
from dtree import DecisionTree
from dtree.models import NodeType

def build_tree(utility_function=None):
    dt = DecisionTree(utility_function=utility_function)
    dt.add_decision_node("I", "Decision")
    dt.add_terminal_node("S", "Sell land", 22_000)
    dt.add_chance_node("D", "Drill land")
    dt.add_edge("I", "S")
    dt.add_edge("I", "D")
    dt.add_decision_node("G", "Gas found")
    dt.add_terminal_node("NG", "No gas found", -40_000)
    dt.add_edge("D", "G", 0.3)
    dt.add_edge("D", "NG", 0.7)
    dt.add_terminal_node("GS", "Sell land to West Gas", 160_000)
    dt.add_chance_node("GD", "Develop the site")
    dt.add_edge("G", "GD")
    dt.add_edge("G", "GS")
    dt.add_terminal_node("NM", "Normal market conditions", 110_000)
    dt.add_terminal_node("GM", "Good market conditions", 260_000)
    dt.add_edge("GD", "NM", 0.4)
    dt.add_edge("GD", "GM", 0.6)
    return dt

def test_decision_tree_methods():
    # Utility function (risk-averse)
    def utility(x):
        return np.cbrt(x).item()

    # Build trees
    dt_raw = build_tree()
    dt_util = build_tree(utility_function=utility)

    # --- Expected values ---
    expected_raw = {
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
    ev_raw = dt_raw.calculate_expected_values()
    ev_util = dt_util.calculate_expected_values()
    for node_id, exp_val in expected_raw.items():
        # Raw tree: expected_value and utility_value are the same
        assert math.isclose(ev_raw[node_id]['expected_value'], exp_val, abs_tol=1e-6)
        assert math.isclose(ev_raw[node_id]['utility_value'], exp_val, abs_tol=1e-6)
        # Utility tree: expected_value matches raw, utility_value is utility-based
        assert math.isclose(ev_util[node_id]['expected_value'], exp_val, abs_tol=1e-6)
        if dt_util.tree_structure.nodes[node_id].node_type == NodeType.TERMINAL:
            expected_utility = utility(exp_val)
            assert math.isclose(ev_util[node_id]['utility_value'], expected_utility, rel_tol=1e-6)
        elif ev_util[node_id]['expected_value'] > 0:
            assert ev_util[node_id]['utility_value'] < ev_util[node_id]['expected_value']

    # --- Optimal path ---
    path_raw = dt_raw.get_optimal_path("I")
    path_util = dt_util.get_optimal_path("I")
    assert path_raw[0] == "I" and dt_raw.tree_structure.nodes[path_raw[-1]].node_type == NodeType.TERMINAL
    assert path_util[0] == "I" and dt_util.tree_structure.nodes[path_util[-1]].node_type == NodeType.TERMINAL

    # --- Children ---
    children_I = dt_raw.get_children("I")
    assert set(children_I) == set([("S", 1.0), ("D", 1.0)])
    children_D = dt_raw.get_children("D")
    assert set(children_D) == set([("G", 0.3), ("NG", 0.7)])
    children_G = dt_raw.get_children("G")
    assert set(children_G) == set([("GD", 1.0), ("GS", 1.0)])
    children_GD = dt_raw.get_children("GD")
    assert set(children_GD) == set([("NM", 0.4), ("GM", 0.6)])

    # --- Raw expected values ---
    raw_ev = dt_util.calculate_raw_expected_values()
    for node_id, exp_val in expected_raw.items():
        assert math.isclose(raw_ev[node_id], exp_val, abs_tol=1e-6)

    # --- Print summary (should not error) ---
    dt_raw.print_tree_summary()
    dt_util.print_tree_summary()

    # --- Mermaid diagram generation (should not error) ---
    dt_raw.generate_mermaid_diagram()
    dt_util.generate_mermaid_diagram() 


def test_decision_tree_with_cbrt_utility():
    import numpy as np
    # Utility function (risk-averse, no .item())
    def utility(x):
        return np.cbrt(x)

    dt_util = build_tree(utility_function=utility)
    ev_util = dt_util.calculate_expected_values()

    expected_raw = {
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
    # Check expected values and utility values
    for node_id, exp_val in expected_raw.items():
        # expected_value should match raw
        assert math.isclose(ev_util[node_id]['expected_value'], exp_val, abs_tol=1e-6)
        # At leaves, utility_value should be np.cbrt(expected_value)
        if dt_util.tree_structure.nodes[node_id].node_type == NodeType.TERMINAL:
            expected_utility = np.cbrt(exp_val)
            assert math.isclose(ev_util[node_id]['utility_value'], expected_utility, rel_tol=1e-6)
        elif ev_util[node_id]['expected_value'] > 0:
            assert ev_util[node_id]['utility_value'] < ev_util[node_id]['expected_value'] 


def test_decision_tree_with_expected_utilities():
    import numpy as np
    def utility(x):
        return np.cbrt(x).item()

    dt_util = build_tree(utility_function=utility)
    ev_util = dt_util.calculate_expected_values()

    expected_util = {
        'I': {'expected_value': 32000.0, 'utility_value': 28.02039330655387},
        'S': {'expected_value': 22000, 'utility_value': 28.02039330655387},
        'D': {'expected_value': 32000.0, 'utility_value': -6.701451687050582},
        'G': {'expected_value': 200000.0, 'utility_value': 57.46070522141058},
        'NG': {'expected_value': -40000, 'utility_value': -34.19951893353394},
        'GS': {'expected_value': 160000, 'utility_value': 54.28835233189813},
        'GD': {'expected_value': 200000.0, 'utility_value': 57.46070522141058},
        'NM': {'expected_value': 110000, 'utility_value': 47.91419857062784},
        'GM': {'expected_value': 260000, 'utility_value': 63.82504298859907}
    }

    for node_id, values in expected_util.items():
        assert math.isclose(ev_util[node_id]['expected_value'], values['expected_value'], abs_tol=1e-6), f"{node_id} expected_value mismatch"
        assert math.isclose(ev_util[node_id]['utility_value'], values['utility_value'], rel_tol=1e-6), f"{node_id} utility_value mismatch" 