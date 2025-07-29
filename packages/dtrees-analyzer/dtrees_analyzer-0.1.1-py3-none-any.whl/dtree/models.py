from typing import Optional
from enum import Enum

class NodeType(Enum):
    DECISION = "decision"
    CHANCE = "chance"
    TERMINAL = "terminal"

class Node:
    def __init__(self, node_id: str, name: str, node_type: NodeType, value: Optional[float] = None):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.value = value  # Only for terminal nodes
        self.expected_value: Optional[float] = None

class Edge:
    def __init__(self, from_node: str, to_node: str, probability: float = 1.0):
        self.from_node = from_node
        self.to_node = to_node
        self.probability = probability