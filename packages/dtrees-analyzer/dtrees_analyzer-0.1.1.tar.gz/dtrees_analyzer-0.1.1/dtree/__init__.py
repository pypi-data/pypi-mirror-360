"""
DTree - A Python package for decision tree analysis and visualization
"""

__version__ = "0.1.0"
__author__ = "Alejandro Daniel Attento"

# Import main classes for easy access
from .core import DecisionTree
from .models import Node, Edge, NodeType

# Define what gets imported with "from decision_tree_analyzer import *"
__all__ = [
    "DecisionTree",
    "Node", 
    "Edge",
    "NodeType"
]