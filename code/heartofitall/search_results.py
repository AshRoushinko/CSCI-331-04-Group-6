# The following code defines a data class for storing / displaying
# a given search algs results

# example output:
# A*: path=['Start', 'Node1', 'Goal'], cost=15.3, expanded=42, time=0.0023s, optimal=True


from dataclasses import dataclass
from typing import List


@dataclass
class SearchResult:
    algorithm_name: str  # name of the alg used
    start: str  # starting city
    goal: str  # goal city
    path: List[str]  # path from start to goal
    cost: float  # total cost of the path
    nodes_expanded: int  # number of nodes expanded during search
    runtime: float  # execution time in seconds
    is_optimal: bool  # whether the path found is optimal or not

    def __str__(self) -> str:
        return (f"{self.algorithm_name}: path={self.path}, cost={self.cost:.1f}, "
                f"expanded={self.nodes_expanded}, time={self.runtime*1000:.3f} ms, "
                f"optimal={self.is_optimal}")