"""
Calculation logic for decision trees
"""
from typing import Dict, Callable, Optional
from .models import TreeStructure, NodeType

class ExpectedValueCalculator:
    """Handles expected value calculations for decision trees"""
    
    def __init__(self, tree_structure: TreeStructure):
        self.tree_structure = tree_structure
    
    def calculate_expected_utilities(self, utility_function: Callable[[float], float]) -> Dict[str, float]:
        """
        Calculate expected utility for all nodes using backward induction (utility function applied at leaves only)
        Returns a dict mapping node_id to expected utility.
        """
        # Reset all expected values
        for node in self.tree_structure.nodes.values():
            node.expected_value = None
        for node_id in self.tree_structure.nodes.keys():
            self._calculate_node_utility(node_id, utility_function)
        return {node_id: node.expected_value for node_id, node in self.tree_structure.nodes.items()}

    def calculate_expected_values(self) -> Dict[str, float]:
        """
        Calculate expected monetary value for all nodes using backward induction (no utility function)
        Returns a dict mapping node_id to expected value.
        """
        for node in self.tree_structure.nodes.values():
            node.expected_value = None
        for node_id in self.tree_structure.nodes.keys():
            self._calculate_node_value(node_id)
        return {node_id: node.expected_value for node_id, node in self.tree_structure.nodes.items()}

    def calculate_both(self, utility_function: Callable[[float], float]) -> Dict[str, dict]:
        """
        Calculate both expected value and expected utility for all nodes.
        Returns a dict mapping node_id to {'expected_value': ..., 'utility_value': ...}
        """
        ev = self.calculate_expected_values()
        eu = self.calculate_expected_utilities(utility_function)
        return {k: {'expected_value': ev[k], 'utility_value': eu[k]} for k in ev}

    def _calculate_node_utility(self, node_id: str, utility_function: Callable[[float], float]) -> float:
        node = self.tree_structure.nodes[node_id]
        if node.expected_value is not None:
            return node.expected_value
        if node.node_type == NodeType.TERMINAL:
            node.expected_value = utility_function(node.value)
        elif node.node_type == NodeType.CHANCE:
            children = self.tree_structure.get_children(node_id)
            node.expected_value = sum(
                prob * self._calculate_node_utility(child_id, utility_function)
                for child_id, prob in children
            )
        elif node.node_type == NodeType.DECISION:
            children = self.tree_structure.get_children(node_id)
            if not children:
                node.expected_value = 0.0
            else:
                node.expected_value = max(
                    self._calculate_node_utility(child_id, utility_function)
                    for child_id, _ in children
                )
        return node.expected_value

    def _calculate_node_value(self, node_id: str) -> float:
        node = self.tree_structure.nodes[node_id]
        if node.expected_value is not None:
            return node.expected_value
        if node.node_type == NodeType.TERMINAL:
            node.expected_value = node.value
        elif node.node_type == NodeType.CHANCE:
            children = self.tree_structure.get_children(node_id)
            node.expected_value = sum(
                prob * self._calculate_node_value(child_id)
                for child_id, prob in children
            )
        elif node.node_type == NodeType.DECISION:
            children = self.tree_structure.get_children(node_id)
            if not children:
                node.expected_value = 0.0
            else:
                node.expected_value = max(
                    self._calculate_node_value(child_id)
                    for child_id, _ in children
                )
        return node.expected_value

class PathFinder:
    """Handles optimal path finding in decision trees"""
    
    def __init__(self, tree_structure: TreeStructure, calculator: ExpectedValueCalculator):
        self.tree_structure = tree_structure
        self.calculator = calculator
    
    def get_optimal_path(self, start_node: str, maximize: bool = True, 
                        utility_function: Optional[Callable[[float], float]] = None) -> list[str]:
        """
        Get the optimal path from a starting node
        
        Args:
            start_node: Starting node ID
            maximize: If True, maximize expected value; if False, minimize
            utility_function: Optional utility function for decision making
            
        Returns:
            List of node IDs representing the optimal path
        """
        if utility_function is not None:
            decision_values = self.calculator.calculate_expected_utilities(utility_function)
        else:
            decision_values = self.calculator.calculate_expected_values()
        path = [start_node]
        current = start_node
        while True:
            node = self.tree_structure.nodes[current]
            children = self.tree_structure.get_children(current)
            if not children:
                break
            if node.node_type in [NodeType.DECISION, NodeType.CHANCE]:
                best_child = None
                best_value = float('-inf') if maximize else float('inf')
                for child_id, _ in children:
                    child_value = decision_values[child_id]
                    if maximize:
                        if child_value > best_value:
                            best_value = child_value
                            best_child = child_id
                    else:
                        if child_value < best_value:
                            best_value = child_value
                            best_child = child_id
                current = best_child
                path.append(current)
            else:
                break
        return path 