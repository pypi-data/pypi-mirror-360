from typing import Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field

class NodeType(Enum):
    DECISION = "decision"
    CHANCE = "chance"
    TERMINAL = "terminal"

@dataclass
class Node:
    """Represents a node in a decision tree"""
    node_id: str
    name: str
    node_type: NodeType
    value: Optional[float] = None
    expected_value: Optional[float] = None
    
    def __post_init__(self):
        """Validate node data after initialization"""
        if not self.node_id or not self.name:
            raise ValueError("Node ID and name cannot be empty")
        
        if self.node_type == NodeType.TERMINAL and self.value is None:
            raise ValueError("Terminal nodes must have a value")
        
        if self.node_type != NodeType.TERMINAL and self.value is not None:
            raise ValueError("Non-terminal nodes should not have a value")

@dataclass
class Edge:
    """Represents an edge between two nodes in a decision tree"""
    from_node: str
    to_node: str
    probability: float = 1.0
    
    def __post_init__(self):
        """Validate edge data after initialization"""
        if not self.from_node or not self.to_node:
            raise ValueError("Edge must connect two valid nodes")
        
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        
        if self.from_node == self.to_node:
            raise ValueError("Edge cannot connect a node to itself")

@dataclass
class TreeStructure:
    """Manages the structure of a decision tree"""
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    
    def add_node(self, node: Node) -> None:
        """Add a node to the tree"""
        if node.node_id in self.nodes:
            raise ValueError(f"Node with ID '{node.node_id}' already exists")
        self.nodes[node.node_id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the tree"""
        if edge.from_node not in self.nodes:
            raise ValueError(f"From node '{edge.from_node}' does not exist")
        if edge.to_node not in self.nodes:
            raise ValueError(f"To node '{edge.to_node}' does not exist")
        self.edges.append(edge)
    
    def get_children(self, node_id: str) -> List[Tuple[str, float]]:
        """Get all children of a node with their probabilities"""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist")
        
        children = []
        for edge in self.edges:
            if edge.from_node == node_id:
                children.append((edge.to_node, edge.probability))
        return children
    
    def get_parents(self, node_id: str) -> List[Tuple[str, float]]:
        """Get all parents of a node with their probabilities"""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist")
        
        parents = []
        for edge in self.edges:
            if edge.to_node == node_id:
                parents.append((edge.from_node, edge.probability))
        return parents
    
    def validate_tree(self) -> bool:
        """Validate that the tree structure is consistent"""
        # Check for isolated nodes
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge.from_node)
            connected_nodes.add(edge.to_node)
        
        for node_id in self.nodes:
            if node_id not in connected_nodes:
                return False
        
        return True