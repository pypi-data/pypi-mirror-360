# ActualCausesIdentification


## Description
This package is designed to identify actual causes in various systems. It implements three algorithms presented in the paper [Searching for actual causes: approximate algorithms with adjustable precision](link_to_paper). Identifying actual causes is crucial for explanability of autonomous and AI based systems.

## Features
- **Beam Search Algorithm**: A modified version of beam search that uses an oracle and a heuristic function to identify actual causes following the HP-definition [1].
- **Iterative Subinstance Algorithm**: Utilizes the Directed Acyclic Graph (DAG) to iteratively search for causes among direct causal parents of the target consequence and through the DAG.
- **Lower Upper Confidence Bounds (LUCB) Algorithm**: Handles the sampling of stochastic oracle functions during beam search, inspired by exploration-only armed bandit methods [2].

## Installation
To install the package, use the following command:
```sh
pip install actualcauses
```

## Usage

### Importing the Package
```python
from actualcauses import find_causes
```

### Example Usage
```python
# Define variables, actual values, and domains
V = ("A", "B", "C") # Variables
v = (1, 1, 0) # Actual values
D = [(0,1), (0,1), (0,1)] # Domains

# Define the target predicate
target = lambda x: x[0] and x[2]

# Define the simulation function (oracle and heuristic functions)
def simulation(interventions):
    # Input: the list of interventions to evaluate
    # Output: (counterfactual state, oracle value, heuristic value) for each intervention
    ret = []
    for intervention in interventions: # Each intervention is a list of variable ID / value pair
        # Compute the variable values in the counterfactual world
        ref = dict(intervention)
        A = ref.get(0, 1)
        B = ref.get(1, 1)
        C = ref.get(2, (not A and B) or (A and not B))
        oracle = A and C
        heuristic = A + B + C
        ret.append(([A, B, C], oracle, heuristic))
    return ret

# Find causes
causes = find_causes(v, D, simulation, V)

# Display the causes
show_rules(causes, V)
```

Output: `C={'A': '0'}, W={}, output=0, score=2.000`

The cause is A with no contingency set. The function also show the values of the oracle (output) and the heuristic (score).

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## References


[1]: Joseph Y. Halpern. A modification of the Halpern-Pearl definition of causality. In Proceedings of the 24th International Conference on Artificial Intelligence, IJCAI’15, pages 3022– 3033. AAAI Press, 2015.

[2]: Emilie Kaufmann and Shivaram Kalyanakrishnan. Information Complexity in Bandit Subset Selection. In Proceedings of the 26th Annual Conference on Learning Theory, pages 228–251. PMLR, June 2013.

## Citation
If you use this work for a scientific publication, please use the following citation:

_Online version comming soon._




