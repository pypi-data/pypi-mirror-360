"""
Main DecisionTree class - orchestrates the different components
"""
from typing import Dict, List, Tuple, Callable, Optional
from .models import Node, Edge, NodeType, TreeStructure
from .calculators import ExpectedValueCalculator, PathFinder
from .formatters import PrecisionFormatter, TreePrinter, MermaidGenerator

# Optional mermaid import for diagram generation
try:
    from mermaid import Mermaid  # type: ignore
except ImportError:  # pragma: no cover
    Mermaid = None  # Fallback when mermaid is not installed

class DecisionTree:
    """
    Main class for creating and analyzing decision trees.
    
    This class orchestrates the different components:
    - TreeStructure: Manages the tree structure
    - ExpectedValueCalculator: Handles calculations
    - PathFinder: Finds optimal paths
    - Formatters: Handle display and formatting
    """
    
    def __init__(self, display_precision: Optional[int] = None, 
                 utility_function: Optional[Callable[[float], float]] = None):
        """
        Initialize a Decision Tree
        
        Args:
            display_precision: Fixed precision for display purposes. If None, will use automatic precision based on significant digits.
            utility_function: Optional function to transform expected values. Should take a float and return a float.
        """
        # Initialize components
        self.tree_structure = TreeStructure()
        self.formatter = PrecisionFormatter(display_precision)
        self.calculator = ExpectedValueCalculator(self.tree_structure)
        self.path_finder = PathFinder(self.tree_structure, self.calculator)
        self.printer = TreePrinter(self.tree_structure, self.formatter)
        self.mermaid_generator = MermaidGenerator(self.tree_structure, self.formatter)
        
        # Store utility function
        self.utility_function = utility_function
        
    def add_decision_node(self, node_id: str, name: str) -> None:
        """Add a decision node to the tree"""
        node = Node(node_id, name, NodeType.DECISION)
        self.tree_structure.add_node(node)
        
    def add_chance_node(self, node_id: str, name: str) -> None:
        """Add a chance node to the tree"""
        node = Node(node_id, name, NodeType.CHANCE)
        self.tree_structure.add_node(node)
        
    def add_terminal_node(self, node_id: str, name: str, value: float) -> None:
        """Add a terminal node to the tree"""
        node = Node(node_id, name, NodeType.TERMINAL, value)
        self.tree_structure.add_node(node)
        
    def add_edge(self, from_node: str, to_node: str, probability: float = 1.0) -> None:
        """Add an edge between two nodes"""
        edge = Edge(from_node, to_node, probability)
        self.tree_structure.add_edge(edge)
        
    def get_children(self, node_id: str) -> List[Tuple[str, float]]:
        """Get all children of a node with their probabilities"""
        return self.tree_structure.get_children(node_id)
        
    def calculate_expected_values(self) -> Dict[str, float] | Dict[str, Dict[str, float]]:
        """
        Calculate expected values for all nodes in the tree using backward induction
        
        Returns:
            If no utility function: Dictionary mapping node_id to expected value
            If utility function present: Dictionary mapping node_id to dict with 'expected_value' and 'utility_value'
        """
        return self.calculator.calculate_expected_values(self.utility_function)
        
    def calculate_raw_expected_values(self) -> Dict[str, float]:
        """
        Calculate expected values for all nodes without applying utility function
        
        Returns:
            Dictionary mapping node_id to raw expected value (without utility function)
        """
        return self.calculator.calculate_raw_expected_values()
        
    def print_tree_summary(self) -> None:
        """Print a summary of the tree with expected values using automatic precision"""
        expected_values = self.calculate_expected_values()
        raw_expected_values = self.calculate_raw_expected_values()
        self.printer.print_tree_summary(expected_values, raw_expected_values, self.utility_function)
        
    def get_optimal_path(self, start_node: str, maximize: bool = True) -> List[str]:
        """
        Get the optimal path from a starting node (for decision nodes)
        
        Args:
            start_node: Starting node ID
            maximize: If True, maximize expected value; if False, minimize expected value
            
        Returns:
            List of node IDs representing the optimal path
        """
        return self.path_finder.get_optimal_path(start_node, maximize, self.utility_function)

    def generate_mermaid_diagram(self, show_expected_values: bool = True) -> str:
        """
        Generate a modern Mermaid diagram representation of the decision tree
        
        Args:
            show_expected_values: Whether to show expected values in nodes
            
        Returns:
            String containing the Mermaid diagram code
        """
        expected_values = self.calculate_expected_values()
        raw_expected_values = self.calculate_raw_expected_values()
        optimal_path_nodes = self.get_optimal_path(next(iter(self.tree_structure.nodes)))
        
        return self.mermaid_generator.generate_diagram(
            expected_values, raw_expected_values, optimal_path_nodes, 
            show_expected_values, self.utility_function
        )
    
    def save_mermaid_diagram(self, filename: str = "decision_tree.md", show_expected_values: bool = True) -> None:
        """
        Save the Mermaid diagram to a markdown file
        
        Args:
            filename: Output filename (should end with .md)
            show_expected_values: Whether to show expected values in nodes
        """
        mermaid_code = self.generate_mermaid_diagram(show_expected_values)
        
        markdown_content = f"""
```mermaid
{mermaid_code}
```
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Mermaid diagram saved to {filename}")

    def save_mermaid_graph(self, filename: str = "decision_tree.png", show_expected_values: bool = True) -> None:
        """
        Save the Mermaid diagram as a PNG image
        
        Args:
            filename: Output filename (should end with .png)
            show_expected_values: Whether to show expected values in nodes
        """
        if Mermaid is None:
            raise ImportError(
                "The 'mermaid' Python package is required for saving graphs as PNG."
                " Install it via 'pip install mermaid' or use 'save_mermaid_diagram' to"
                " export a markdown diagram instead."
            )

        mermaid_code = self.generate_mermaid_diagram(show_expected_values)
        mermaid = Mermaid(mermaid_code)
        mermaid.to_png(filename)