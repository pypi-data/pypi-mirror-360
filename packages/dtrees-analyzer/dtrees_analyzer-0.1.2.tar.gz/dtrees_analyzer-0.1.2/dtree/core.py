import math
from typing import Dict, List, Tuple, Callable, Optional
from .models import Node, Edge, NodeType
# Optional mermaid import for diagram generation
try:
    from mermaid import Mermaid  # type: ignore
except ImportError:  # pragma: no cover
    Mermaid = None  # Fallback when mermaid is not installed

class DecisionTree:
    def __init__(self, display_precision: int = None, utility_function: Optional[Callable[[float], float]] = None):
        """
        Initialize a Decision Tree
        
        Args:
            display_precision: Fixed precision for display purposes. If None, will use automatic precision based on significant digits.
            utility_function: Optional function to transform expected values. Should take a float and return a float.
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.display_precision = display_precision
        self.utility_function = utility_function
        
    def _apply_utility_function(self, value: float) -> float:
        """
        Apply utility function to a value if one is defined
        
        Args:
            value: The value to transform
            
        Returns:
            Transformed value or original value if no utility function
        """
        if self.utility_function is not None:
            return self.utility_function(value)
        return value
        
    def _calculate_significant_digits(self, value: float) -> int:
        """
        Calculate the number of significant digits needed for a value
        
        Args:
            value: The numeric value to analyze
            
        Returns:
            Number of decimal places needed to preserve significant digits
        """
        if value == 0:
            return 2
        
        # Get the magnitude of the number
        magnitude = math.floor(math.log10(abs(value)))
        
        # For values >= 1, use 2 decimal places minimum
        if magnitude >= 0:
            return max(2, 3 - magnitude)
        
        # For values < 1, use enough decimals to show significant digits
        return abs(magnitude) + 2
    
    def _get_display_precision(self, values: List[float] = None) -> int:
        """
        Get the appropriate display precision
        
        Args:
            values: List of values to analyze for automatic precision
            
        Returns:
            Number of decimal places to use for display
        """
        if self.display_precision is not None:
            return self.display_precision
        
        if values is None or len(values) == 0:
            return 2
        
        # Calculate precision needed for all values
        precisions = [self._calculate_significant_digits(v) for v in values if v != 0]
        
        if not precisions:
            return 2
        
        # Use the maximum precision needed, but cap at 6 decimal places
        return min(max(precisions), 6)
    
    def _format_probability_as_percentage(self, probability: float) -> str:
        """
        Format probability as percentage
        
        Args:
            probability: Probability value (0.0 to 1.0)
            
        Returns:
            Formatted percentage string
        """
        percentage = probability * 100
        
        # Use appropriate precision for percentages
        if percentage == 100.0:
            return "100%"
        elif percentage >= 10:
            return f"{percentage:.1f}%"
        elif percentage >= 1:
            return f"{percentage:.2f}%"
        else:
            return f"{percentage:.3f}%"
        
    def add_decision_node(self, node_id: str, name: str):
        """Add a decision node to the tree"""
        self.nodes[node_id] = Node(node_id, name, NodeType.DECISION)
        
    def add_chance_node(self, node_id: str, name: str):
        """Add a chance node to the tree"""
        self.nodes[node_id] = Node(node_id, name, NodeType.CHANCE)
        
    def add_terminal_node(self, node_id: str, name: str, value: float):
        """Add a terminal node to the tree"""
        self.nodes[node_id] = Node(node_id, name, NodeType.TERMINAL, value)
        
    def add_edge(self, from_node: str, to_node: str, probability: float = 1.0):
        """Add an edge between two nodes"""
        if from_node not in self.nodes:
            raise ValueError(f"From node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"To node '{to_node}' does not exist")
            
        self.edges.append(Edge(from_node, to_node, probability))
        
    def get_children(self, node_id: str) -> List[Tuple[str, float]]:
        """Get all children of a node with their probabilities"""
        children = []
        for edge in self.edges:
            if edge.from_node == node_id:
                children.append((edge.to_node, edge.probability))
        return children
        
    def calculate_expected_values(self) -> Dict[str, float] | Dict[str, Dict[str, float]]:
        """
        Calculate expected values for all nodes in the tree using backward induction
        Internal calculations use full precision, no rounding applied
        
        Returns:
            If no utility function: Dictionary mapping node_id to expected value
            If utility function present: Dictionary mapping node_id to dict with 'expected_value' and 'utility_value'
        """
        # Reset all expected values
        for node in self.nodes.values():
            node.expected_value = None
            
        def calculate_node_value(node_id: str) -> float:
            node = self.nodes[node_id]
            
            # Return cached value if already calculated
            if node.expected_value is not None:
                return node.expected_value
                
            if node.node_type == NodeType.TERMINAL:
                node.expected_value = node.value
                
            elif node.node_type == NodeType.CHANCE:
                children = self.get_children(node_id)
                expected_value = 0.0
                
                for child_id, probability in children:
                    child_value = calculate_node_value(child_id)
                    expected_value += probability * child_value
                    
                node.expected_value = expected_value
                
            elif node.node_type == NodeType.DECISION:
                children = self.get_children(node_id)
                if not children:
                    node.expected_value = 0.0
                else:
                    # For decision nodes, take the maximum expected value
                    max_value = float('-inf')
                    for child_id, _ in children:
                        child_value = calculate_node_value(child_id)
                        max_value = max(max_value, child_value)
                    node.expected_value = max_value
                    
            return node.expected_value
            
        # Calculate expected values for all nodes
        for node_id in self.nodes.keys():
            calculate_node_value(node_id)
            
        # Return results based on whether utility function is present
        results = {}
        for node_id, node in self.nodes.items():
            if self.utility_function is not None:
                results[node_id] = {
                    'expected_value': node.expected_value,
                    'utility_value': self._apply_utility_function(node.expected_value)
                }
            else:
                results[node_id] = node.expected_value
            
        return results
        
    def calculate_raw_expected_values(self) -> Dict[str, float]:
        """
        Calculate expected values for all nodes without applying utility function
        This is used for display purposes to show both utility and raw expected values
        
        Returns:
            Dictionary mapping node_id to raw expected value (without utility function)
        """
        # Reset all expected values
        for node in self.nodes.values():
            node.expected_value = None
            
        def calculate_node_value(node_id: str) -> float:
            node = self.nodes[node_id]
            
            # Return cached value if already calculated
            if node.expected_value is not None:
                return node.expected_value
                
            if node.node_type == NodeType.TERMINAL:
                node.expected_value = node.value
                
            elif node.node_type == NodeType.CHANCE:
                children = self.get_children(node_id)
                expected_value = 0.0
                
                for child_id, probability in children:
                    child_value = calculate_node_value(child_id)
                    expected_value += probability * child_value
                    
                node.expected_value = expected_value
                
            elif node.node_type == NodeType.DECISION:
                children = self.get_children(node_id)
                if not children:
                    node.expected_value = 0.0
                else:
                    # For decision nodes, take the maximum expected value
                    max_value = float('-inf')
                    for child_id, _ in children:
                        child_value = calculate_node_value(child_id)
                        max_value = max(max_value, child_value)
                    node.expected_value = max_value
                    
            return node.expected_value
            
        # Calculate expected values for all nodes
        for node_id in self.nodes.keys():
            calculate_node_value(node_id)
            
        # Return raw results without utility function
        results = {}
        for node_id, node in self.nodes.items():
            results[node_id] = node.expected_value
            
        return results
        
    def print_tree_summary(self):
        """Print a summary of the tree with expected values using automatic precision"""
        expected_values = self.calculate_expected_values()
        raw_expected_values = self.calculate_raw_expected_values()
        
        # Get all values for precision calculation
        all_values = []
        for node in self.nodes.values():
            if node.node_type == NodeType.TERMINAL:
                all_values.append(node.value)
        all_values.extend(raw_expected_values.values())
        if self.utility_function is not None:
            # Extract utility values for precision calculation
            utility_values = [v['utility_value'] for v in expected_values.values() if isinstance(v, dict)]
            all_values.extend(utility_values)
        
        # Get appropriate display precision
        precision = self._get_display_precision(all_values)
        
        print("Decision Tree Summary:")
        print("=" * 50)
        
        for node_id, node in self.nodes.items():
            print(f"{node.node_type.value.upper()}: {node.name} ({node_id})")
            if node.node_type == NodeType.TERMINAL:
                print(f"  Terminal Value: {node.value:,.{precision}f}")
                if self.utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    print(f"  Utility Value: {utility_val:,.{precision}f}")
                    print(f"  Expected Value: {raw_ev:,.{precision}f}")
                else:
                    print(f"  Expected Value: {expected_values[node_id]:,.{precision}f}")
            else:
                # Show expected values for non-terminal nodes
                if self.utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    print(f"  Utility Value: {utility_val:,.{precision}f}")
                    print(f"  Expected Value: {raw_ev:,.{precision}f}")
                else:
                    print(f"  Expected Value: {expected_values[node_id]:,.{precision}f}")
            
            # Show children
            children = self.get_children(node_id)
            if children:
                print("  Children:")
                for child_id, prob in children:
                    child_name = self.nodes[child_id].name
                    prob_str = self._format_probability_as_percentage(prob)
                    print(f"    -> {child_name} ({child_id}) [{prob_str}]")
            print()
        
    def get_optimal_path(self, start_node: str, maximize: bool = True) -> List[str]:
        """
        Get the optimal path from a starting node (for decision nodes)
        
        Args:
            start_node: Starting node ID
            maximize: If True, maximize expected value; if False, minimize expected value
            
        Returns:
            List of node IDs representing the optimal path
        """
        # Use utility values for decision making if utility function is present
        if self.utility_function is not None:
            expected_values = self.calculate_expected_values()  # This returns dict with both values
            # Extract utility values for decision making
            decision_values = {node_id: values['utility_value'] if isinstance(values, dict) else values 
                             for node_id, values in expected_values.items()}
        else:
            decision_values = self.calculate_raw_expected_values()  # This returns raw expected values
            
        path = [start_node]
        current = start_node
        
        while True:
            node = self.nodes[current]
            children = self.get_children(current)
            
            if not children:  # Terminal node
                break
                
            if node.node_type == NodeType.DECISION:
                # Choose child with optimal expected value based on maximize parameter
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
                
            elif node.node_type == NodeType.CHANCE:
                # For chance nodes, also choose the optimal child based on expected values
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

    def generate_mermaid_diagram(self, show_expected_values: bool = True) -> str:
        """
        Generate a modern Mermaid diagram representation of the decision tree
        
        Args:
            show_expected_values: Whether to show expected values in nodes
            
        Returns:
            String containing the Mermaid diagram code
        """
        # Calculate expected values first
        expected_values = self.calculate_expected_values()
        raw_expected_values = self.calculate_raw_expected_values()
        
        # Get all values for precision calculation
        all_values = []
        for node in self.nodes.values():
            if node.node_type == NodeType.TERMINAL:
                all_values.append(node.value)
        all_values.extend(raw_expected_values.values())
        if self.utility_function is not None:
            # Extract utility values for precision calculation
            utility_values = [v['utility_value'] for v in expected_values.values() if isinstance(v, dict)]
            all_values.extend(utility_values)
        
        # Get appropriate display precision
        precision = self._get_display_precision(all_values)
        
        # Compute the optimal path (as a set of edges)
        optimal_path_nodes = self.get_optimal_path(next(iter(self.nodes)))
        optimal_path_edges = set()
        for i in range(len(optimal_path_nodes) - 1):
            optimal_path_edges.add((optimal_path_nodes[i], optimal_path_nodes[i+1]))
        
        # Start with horizontal layout
        mermaid_code = ["graph LR"]
        
        # Define modern Tableau-like node styles
        mermaid_code.extend([
            # Decision nodes - Blue theme
            "    classDef decision fill:#4e79a7,stroke:#2c5f85,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px",
            # Chance nodes - Orange theme  
            "    classDef chance fill:#f28e2c,stroke:#d4751a,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px",
            # Terminal nodes - Green theme
            "    classDef terminal fill:#59a14f,stroke:#3f7a37,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px",
        ])
        
        # Add nodes with enhanced styling
        for node_id, node in self.nodes.items():
            label_parts = [f"<b>{node.name}</b>"]
            
            # Add values to label with better formatting
            if node.node_type == NodeType.TERMINAL:
                if self.utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    label_parts.append(f"U: {utility_val:,.{precision}f}")
                    label_parts.append(f"EV: {raw_ev:,.{precision}f}")
                else:
                    label_parts.append(f"EV: {node.value:,.{precision}f}")
            elif show_expected_values and node_id in expected_values:
                if self.utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    label_parts.append(f"U: {utility_val:,.{precision}f}")
                    label_parts.append(f"EV: {raw_ev:,.{precision}f}")
                else:
                    label_parts.append(f"EV: {expected_values[node_id]:,.{precision}f}")
            
            # Create label with line breaks
            label = "<br/>".join(label_parts)
            
            # Determine node shape based on type with modern styling
            if node.node_type == NodeType.DECISION:
                # Rounded rectangle for decision nodes (more modern than diamond)
                mermaid_code.append(f'    {node_id}["{label}"]')
                mermaid_code.append(f"    class {node_id} decision")
            elif node.node_type == NodeType.CHANCE:
                # Stadium shape for chance nodes (modern rounded pill shape)
                mermaid_code.append(f'    {node_id}(["{label}"])')
                mermaid_code.append(f"    class {node_id} chance")
            else:  # Terminal
                # Rounded rectangle for terminal nodes
                mermaid_code.append(f'    {node_id}["{label}"]')
                mermaid_code.append(f"    class {node_id} terminal")
        
        # Add edges with enhanced styling
        link_styles = []
        edge_count = 0
        for edge in self.edges:
            # Format probability as percentage
            if edge.probability == 1.0:
                prob_label = ""
            else:
                prob_str = self._format_probability_as_percentage(edge.probability)
                prob_label = f"|<b>{prob_str}</b>|"
            
            edge_str = f"    {edge.from_node} ==>{prob_label} {edge.to_node}"
            mermaid_code.append(edge_str)
            # If this edge is in the optimal path, add a custom linkStyle
            if (edge.from_node, edge.to_node) in optimal_path_edges:
                link_styles.append(f"    linkStyle {edge_count} stroke:#e15759,stroke-width:5px;")
            edge_count += 1
        
        # Add overall styling
        mermaid_code.extend([
            "    linkStyle default stroke:#666,stroke-width:2px",
            "    %%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#333333', 'primaryBorderColor':'#dddddd', 'lineColor':'#666666'}}}%%"
        ])
        # Add custom link styles for optimal path
        mermaid_code.extend(link_styles)
        
        return "\n".join(mermaid_code)
    
    def save_mermaid_diagram(self, filename: str = "decision_tree.md", show_expected_values: bool = True):
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

    def save_mermaid_graph(self, filename: str = "decision_tree.png", show_expected_values: bool = True):
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