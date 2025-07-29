<div align="center">
  <img src="./images/logo.png" width="500" alt="Logo">
</div>

# DTrees: Decision Tree Analyzer

A Python package for creating, analyzing, and visualizing decision trees.

In case of questions or ideas to improve the library, reach out to me at:
* [Email](alejandro@thebyte.guru)
* [LinkedIn](https://www.linkedin.com/in/alejandro-daniel-attento/)

Forks are welcome, but reach out to me to discuss the updates.

# Install

To install the library run 
```bash
!pip install dtrees-analyzer
```

For more information about versions, changes, etc., visit the [project page](https://pypi.org/project/dtrees-analyzer/) on PyPI.

## Usage

#### For the decision tree you only need to provide a utility function if one is used:
* **utility_function**: Utility function, should take a float value as input

#### For each node you need to add the following parameters:
* **node_id**: The ID used to connect and identify nodes
* **node_name**: The name of the node to describe it, shown in the graphs
* **value**: The value of the node, applies only to terminal nodes

#### For each edge you need to add the following parameters:
* **from_node**: The starting node
* **to_node**: The node it should be connected to
* **probability**: The probability between two nodes, applies only if:
    * Chance node is connected to Chance node
    * Chance node is connected to Terminal node


### The way to describe a decision tree using the library is by:

1. **Defining the decision tree**  
If you want to use a utility function, you should provide it at the decision tree definition.
```python
dt = DecisionTree()

# def any_utility_function(x: float):
#     return <Some utility function>
# dt = DecisionTree(utility_function=any_utility_function)
```

2. **Adding decision nodes**
For these nodes we don't know the probabilities for each option as they are decisions we have to make. When calculating the expected values (EV) based on the child nodes, it will always take the node with the highest expected value (or utility value if a function is provided).

```python
dt.add_decision_node("I", "Decision")
```

3. **Adding chance nodes**
These are intermediate nodes which direct us to other nodes based on a certain probability.
```python
dt.add_chance_node("B", "Buy TSLA stocks")
```

4. **Adding terminal nodes**
These nodes are final nodes which are associated with the known expected value we have for each branch.
```python
dt.add_terminal_node("PI", "The price increases", 1_000)
```
5. **Adding edges between nodes**
These are the connections between the nodes, and in the case of chance nodes connected among them or to terminal nodes, they will be associated with probabilities.
```python
# Connecting nodes with probability [Chance node -> Chance node & Chance node -> Terminal node]
dt.add_edge("P", "PE", 0.3)

# Connecting nodes without probability [Decision node -> Any]
dt.add_edge("I", "B")
```

For each node you have to add the following parameters:
* **node_id**: The ID used to connect and identify nodes
* **node_name**: The name of the node to describe it, shown in the graphs
* **value**: The value of the node, applies only to terminal nodes

### Example

```python
# Define decision tree
dt = DecisionTree()

# Build decision tree
dt.add_decision_node("D", "Decision")
dt.add_chance_node("B", "Buy TSLA stocks")
dt.add_terminal_node("NB", "Don't buy TSLA stocks", 0)
dt.add_edge("D", "B")
dt.add_edge("D", "NB")

dt.add_terminal_node("PI", "The price increases", 1_000)
dt.add_terminal_node("PD", "The price decreases", -2_000)
dt.add_edge("B", "PI", 0.6)
dt.add_edge("B", "PD", 0.4)

dt.save_mermaid_graph("./images/example.png")
```
![Example](./images/example.png)


## Comprehensive Example: Land Investment Decision

Newox is considering whether or not to drill on its own land in search of natural gas. If the company decides to drill, the cost is $40,000. If gas is found, Newox has two options: it can either sell the land to West Gas for $200,000 or develop the site itself. If no gas is found, there are no additional costs or revenues beyond the initial drilling cost.

The other option is to skip drilling entirely and sell the land as-is for $22,000.

At current natural gas prices, a producing well would be worth $150,000 on the open market. However, there's a chance gas prices could double, in which case the well would be worth $300,000.

Company engineers estimate a 30% chance of finding gas. Meanwhile, the company's economist believes there's a 60% chance that gas prices will double.

What decision should Newox make to maximize its expected profits?

*This example demonstrates a more complex decision tree for a land investment scenario, both with and without a utility function.*

### Without Utility Function

```python
from dtree import DecisionTree

# Create decision tree
dt = DecisionTree()

# Add nodes
dt.add_decision_node("I", "Decision")
dt.add_terminal_node("S", "Sell land", 22_000)
dt.add_chance_node("D", "Drill land")
dt.add_edge("I", "S")
dt.add_edge("I", "D")

dt.add_decision_node("G", "Gas found")
dt.add_terminal_node("NG", "No gas found", -40_000)
dt.add_edge("D", "G", 0.3)
dt.add_edge("D", "NG", 0.7)

dt.add_terminal_node("GS", "Sell land to West Gas", 200_000-40_000)
dt.add_chance_node("GD", "Develop the site")
dt.add_edge("G", "GD")
dt.add_edge("G", "GS")

dt.add_terminal_node("NM", "Normal market conditions", 150_000-40_000)
dt.add_terminal_node("GM", "Good market conditions", 300_000-40_000)
dt.add_edge("GD", "NM", 0.4)
dt.add_edge("GD", "GM", 0.6)

# Create graph
dt.save_mermaid_graph("./images/case_without_utility_func.png")
```
![Case without utility function](./images/case_without_utility_func.png)

### With Utility Function

The utility function is:
## $u(x) = \sqrt[3]{x}$

```python
import numpy as np
from dtree import DecisionTree

# Utility function
def utility(x):
    return np.cbrt(x)

# Create decision tree
dt = DecisionTree(utility_function=utility)

# Add nodes
dt.add_decision_node("I", "Decision")
dt.add_terminal_node("S", "Sell land", 22_000)
dt.add_chance_node("D", "Drill land")
dt.add_edge("I", "S")
dt.add_edge("I", "D")

dt.add_decision_node("G", "Gas found")
dt.add_terminal_node("NG", "No gas found", -40_000)
dt.add_edge("D", "G", 0.3)
dt.add_edge("D", "NG", 0.7)

dt.add_terminal_node("GS", "Sell land to West Gas", 200_000-40_000)
dt.add_chance_node("GD", "Develop the site")
dt.add_edge("G", "GD")
dt.add_edge("G", "GS")

dt.add_terminal_node("NM", "Normal market conditions", 150_000-40_000)
dt.add_terminal_node("GM", "Good market conditions", 300_000-40_000)
dt.add_edge("GD", "NM", 0.4)
dt.add_edge("GD", "GM", 0.6)
```

#### To analyze the decision tree you can:

Create a mermaid graph using `save_mermaid_graph`.  
*The thicker line shows the optimal path. This is useful to understand, at each decision node, which would be the best path given the quantified information.*
```python
dt.save_mermaid_graph("./images/case_with_utility_func.png")
```
![Case with utility function](./images/case_with_utility_func.png)

Create a markdown representation of the mermaid graph using `save_mermaid_diagram`. So, you can customize the graph using services as [Mermaid.live](https://mermaid.live/).
```python
dt.save_mermaid_diagram("./images/case_with_utility_func.md")

# Output
# graph LR
#     classDef decision fill:#4e79a7,stroke:#2c5f85,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px
#     classDef chance fill:#f28e2c,stroke:#d4751a,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px
#     classDef terminal fill:#59a14f,stroke:#3f7a37,stroke-width:3px,color:#ffffff,font-weight:bold,font-size:12px
#     I["<b>Decision</b><br/>U: 31.75<br/>EV: 32,000.00"]
#     class I decision
#     S["<b>Sell land</b><br/>U: 28.02<br/>EV: 22,000.00"]
#     class S terminal
#     D(["<b>Drill land</b><br/>U: 31.75<br/>EV: 32,000.00"])
#     class D chance
#     G["<b>Gas found</b><br/>U: 58.48<br/>EV: 200,000.00"]
#     class G decision
#     NG["<b>No gas found</b><br/>U: -34.20<br/>EV: -40,000.00"]
#     class NG terminal
#     GS["<b>Sell land to West Gas</b><br/>U: 54.29<br/>EV: 160,000.00"]
#     class GS terminal
#     GD(["<b>Develop the site</b><br/>U: 58.48<br/>EV: 200,000.00"])
#     class GD chance
#     NM["<b>Normal market conditions</b><br/>U: 47.91<br/>EV: 110,000.00"]
#     class NM terminal
#     GM["<b>Good market conditions</b><br/>U: 63.83<br/>EV: 260,000.00"]
#     class GM terminal
#     I ==> S
#     I ==> D
#     D ==>|<b>30.0%</b>| G
#     D ==>|<b>70.0%</b>| NG
#     G ==> GD
#     G ==> GS
#     GD ==>|<b>40.0%</b>| NM
#     GD ==>|<b>60.0%</b>| GM
#     linkStyle default stroke:#666,stroke-width:2px
#     %%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#333333', 'primaryBorderColor':'#dddddd', 'lineColor':'#666666'}}}%%
#     linkStyle 1 stroke:#e15759,stroke-width:5px;
#     linkStyle 2 stroke:#e15759,stroke-width:5px;
#     linkStyle 4 stroke:#e15759,stroke-width:5px;
#     linkStyle 7 stroke:#e15759,stroke-width:5px;
```

The `calculate_expected_values` method allows you to get all the values as a dictionary.
```python
# Expected output
dt.calculate_expected_values()

# Output
# {
#     'I': {'expected_value': 32000.0, 'utility_value': 31.74802103936399},
#     'S': {'expected_value': 22000, 'utility_value': 28.02039330655387},
#     'D': {'expected_value': 32000.0, 'utility_value': 31.74802103936399},
#     'G': {'expected_value': 200000.0, 'utility_value': 58.480354764257314},
#     'NG': {'expected_value': -40000, 'utility_value': -34.19951893353394},
#     'GS': {'expected_value': 160000, 'utility_value': 54.28835233189813},
#     'GD': {'expected_value': 200000.0, 'utility_value': 58.480354764257314},
#     'NM': {'expected_value': 110000, 'utility_value': 47.91419857062784},
#     'GM': {'expected_value': 260000, 'utility_value': 63.82504298859907}
# }
```

The `get_optimal_path` allows you to get the optimal path based on a starting node.
```python
dt.get_optimal_path("I")

# Output
# ['I', 'D', 'G', 'GD', 'GM']
```

The `get_children` method shows you all the child nodes based on a node ID you provide.
```python
dt.get_children("GD")

# Output
# [
#     ('NM', 0.4), 
#     ('GM', 0.6)
# ]
```
