"""
Calculation logic for decision trees
"""
from typing import Dict, Callable, Optional
from .models import TreeStructure, NodeType

class ExpectedValueCalculator:
    """Handles expected value calculations for decision trees"""
    
    def __init__(self, tree_structure: TreeStructure):
        self.tree_structure = tree_structure
    
    def calculate_expected_values(self, utility_function: Optional[Callable[[float], float]] = None) -> Dict[str, float] | Dict[str, Dict[str, float]]:
        """
        Calculate expected values for all nodes using backward induction
        
        Args:
            utility_function: Optional function to transform expected values
            
        Returns:
            Dictionary mapping node_id to expected value or dict with both raw and utility values
        """
        # Reset all expected values
        for node in self.tree_structure.nodes.values():
            node.expected_value = None
            
        # Calculate expected values for all nodes
        for node_id in self.tree_structure.nodes.keys():
            self._calculate_node_value(node_id)
            
        # Return results based on whether utility function is present
        results = {}
        for node_id, node in self.tree_structure.nodes.items():
            if utility_function is not None:
                results[node_id] = {
                    'expected_value': node.expected_value,
                    'utility_value': utility_function(node.expected_value)
                }
            else:
                results[node_id] = node.expected_value
            
        return results
    
    def calculate_raw_expected_values(self) -> Dict[str, float]:
        """
        Calculate expected values without applying utility function
        
        Returns:
            Dictionary mapping node_id to raw expected value
        """
        return self.calculate_expected_values(utility_function=None)
    
    def _calculate_node_value(self, node_id: str) -> float:
        """Calculate expected value for a specific node"""
        node = self.tree_structure.nodes[node_id]
        
        # Return cached value if already calculated
        if node.expected_value is not None:
            return node.expected_value
            
        if node.node_type == NodeType.TERMINAL:
            node.expected_value = node.value
            
        elif node.node_type == NodeType.CHANCE:
            children = self.tree_structure.get_children(node_id)
            expected_value = 0.0
            
            for child_id, probability in children:
                child_value = self._calculate_node_value(child_id)
                expected_value += probability * child_value
                
            node.expected_value = expected_value
            
        elif node.node_type == NodeType.DECISION:
            children = self.tree_structure.get_children(node_id)
            if not children:
                node.expected_value = 0.0
            else:
                # For decision nodes, take the maximum expected value
                max_value = float('-inf')
                for child_id, _ in children:
                    child_value = self._calculate_node_value(child_id)
                    max_value = max(max_value, child_value)
                node.expected_value = max_value
                
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
        # Get decision values (with or without utility function)
        if utility_function is not None:
            expected_values = self.calculator.calculate_expected_values(utility_function)
            decision_values = {node_id: values['utility_value'] if isinstance(values, dict) else values 
                             for node_id, values in expected_values.items()}
        else:
            decision_values = self.calculator.calculate_raw_expected_values()
            
        path = [start_node]
        current = start_node
        
        while True:
            node = self.tree_structure.nodes[current]
            children = self.tree_structure.get_children(current)
            
            if not children:  # Terminal node
                break
                
            if node.node_type in [NodeType.DECISION, NodeType.CHANCE]:
                # Choose child with optimal expected value
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
            else:  # Terminal
                break
                
        return path 