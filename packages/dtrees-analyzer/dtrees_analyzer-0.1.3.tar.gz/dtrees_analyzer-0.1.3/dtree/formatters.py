"""
Formatting and display logic for decision trees
"""
import math
from typing import List, Dict, Callable, Optional
from .models import TreeStructure, NodeType

class PrecisionFormatter:
    """Handles precision formatting for display purposes"""
    
    def __init__(self, display_precision: Optional[int] = None):
        self.display_precision = display_precision
    
    def _calculate_significant_digits(self, value: float) -> int:
        """Calculate the number of significant digits needed for a value"""
        if value == 0:
            return 2
        
        # Get the magnitude of the number
        magnitude = math.floor(math.log10(abs(value)))
        
        # For values >= 1, use 2 decimal places minimum
        if magnitude >= 0:
            return max(2, 3 - magnitude)
        
        # For values < 1, use enough decimals to show significant digits
        return abs(magnitude) + 2
    
    def get_display_precision(self, values: List[float] = None) -> int:
        """Get the appropriate display precision"""
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
    
    def format_probability_as_percentage(self, probability: float) -> str:
        """Format probability as percentage"""
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

class TreePrinter:
    """Handles printing and text representation of decision trees"""
    
    def __init__(self, tree_structure: TreeStructure, formatter: PrecisionFormatter):
        self.tree_structure = tree_structure
        self.formatter = formatter
    
    def print_tree_summary(self, expected_values: Dict, raw_expected_values: Dict, 
                          utility_function: Optional[Callable[[float], float]] = None):
        """Print a summary of the tree with expected values"""
        # Get all values for precision calculation
        all_values = []
        for node in self.tree_structure.nodes.values():
            if node.node_type == NodeType.TERMINAL:
                all_values.append(node.value)
        all_values.extend(raw_expected_values.values())
        if utility_function is not None:
            # Extract utility values for precision calculation
            utility_values = [v['utility_value'] for v in expected_values.values() if isinstance(v, dict)]
            all_values.extend(utility_values)
        
        # Get appropriate display precision
        precision = self.formatter.get_display_precision(all_values)
        
        print("Decision Tree Summary:")
        print("=" * 50)
        
        for node_id, node in self.tree_structure.nodes.items():
            print(f"{node.node_type.value.upper()}: {node.name} ({node_id})")
            if node.node_type == NodeType.TERMINAL:
                print(f"  Terminal Value: {node.value:,.{precision}f}")
                if utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    print(f"  Utility Value: {utility_val:,.{precision}f}")
                    print(f"  Expected Value: {raw_ev:,.{precision}f}")
                else:
                    print(f"  Expected Value: {expected_values[node_id]:,.{precision}f}")
            else:
                # Show expected values for non-terminal nodes
                if utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    print(f"  Utility Value: {utility_val:,.{precision}f}")
                    print(f"  Expected Value: {raw_ev:,.{precision}f}")
                else:
                    print(f"  Expected Value: {expected_values[node_id]:,.{precision}f}")
            
            # Show children
            children = self.tree_structure.get_children(node_id)
            if children:
                print("  Children:")
                for child_id, prob in children:
                    child_name = self.tree_structure.nodes[child_id].name
                    prob_str = self.formatter.format_probability_as_percentage(prob)
                    print(f"    -> {child_name} ({child_id}) [{prob_str}]")
            print()

class MermaidGenerator:
    """Handles Mermaid diagram generation"""
    
    def __init__(self, tree_structure: TreeStructure, formatter: PrecisionFormatter):
        self.tree_structure = tree_structure
        self.formatter = formatter
    
    def generate_diagram(self, expected_values: Dict, raw_expected_values: Dict,
                        optimal_path_nodes: List[str], show_expected_values: bool = True,
                        utility_function: Optional[Callable[[float], float]] = None) -> str:
        """Generate a Mermaid diagram representation of the decision tree"""
        # Get all values for precision calculation
        all_values = []
        for node in self.tree_structure.nodes.values():
            if node.node_type == NodeType.TERMINAL:
                all_values.append(node.value)
        all_values.extend(raw_expected_values.values())
        if utility_function is not None:
            # Extract utility values for precision calculation
            utility_values = [v['utility_value'] for v in expected_values.values() if isinstance(v, dict)]
            all_values.extend(utility_values)
        
        # Get appropriate display precision
        precision = self.formatter.get_display_precision(all_values)
        
        # Compute the optimal path (as a set of edges)
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
        for node_id, node in self.tree_structure.nodes.items():
            label_parts = [f"<b>{node.name}</b>"]
            
            # Add values to label with better formatting
            if node.node_type == NodeType.TERMINAL:
                if utility_function is not None:
                    utility_val = expected_values[node_id]['utility_value']
                    raw_ev = expected_values[node_id]['expected_value']
                    label_parts.append(f"U: {utility_val:,.{precision}f}")
                    label_parts.append(f"EV: {raw_ev:,.{precision}f}")
                else:
                    label_parts.append(f"EV: {node.value:,.{precision}f}")
            elif show_expected_values and node_id in expected_values:
                if utility_function is not None:
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
        for edge in self.tree_structure.edges:
            # Format probability as percentage
            if edge.probability == 1.0:
                prob_label = ""
            else:
                prob_str = self.formatter.format_probability_as_percentage(edge.probability)
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