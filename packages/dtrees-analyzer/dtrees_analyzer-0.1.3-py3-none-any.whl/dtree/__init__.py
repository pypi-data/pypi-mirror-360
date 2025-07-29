"""
DTree - A Python package for decision tree analysis and visualization
"""

__version__ = "0.1.1"
__author__ = "Alejandro Daniel Attento"

# Import main classes for easy access
from .core import DecisionTree
from .models import Node, Edge, NodeType, TreeStructure
from .calculators import ExpectedValueCalculator, PathFinder
from .formatters import PrecisionFormatter, TreePrinter, MermaidGenerator

# Define what gets imported with "from dtree import *"
__all__ = [
    "DecisionTree",
    "Node", 
    "Edge",
    "NodeType",
    "TreeStructure",
    "ExpectedValueCalculator",
    "PathFinder",
    "PrecisionFormatter",
    "TreePrinter",
    "MermaidGenerator"
]