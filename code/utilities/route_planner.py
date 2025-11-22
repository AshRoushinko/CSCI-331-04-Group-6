# code/utilities/route_planner.py
"""
Route Planner controller

Bridges the GUI and the search algorithms. Given a Graph, it can run one
or many algorithms and return comparable SearchResult objects.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Resilient imports: work whether you're running as a package or flat files
try:
    from code.algorithms.bfs import BFS
    from code.algorithms.dfs import DFS
    from code.algorithms.ucs import UCS
    from code.algorithms.greedy import GreedyBestFirst
    from code.algorithms.astar import AStar
    from code.algorithms.ids import IDS
    from code.heartofitall.graph import Graph
    from code.heartofitall.search_results import SearchResult
except Exception:  # pragma: no cover
    from code.algorithms.bfs import BFS
    from code.algorithms.dfs import DFS
    from code.algorithms.ucs import UCS
    from code.algorithms.greedy import GreedyBestFirst
    from code.algorithms.astar import AStar
    from code.algorithms.ids import IDS
    from code.heartofitall.graph import Graph
    from code.heartofitall.search_results import SearchResult

ALGO_REGISTRY: Dict[str, Callable[[Graph, str, str], "SearchAlgorithm"]] = {
    "DFS": DFS,
    "BFS": BFS,
    "UCS": UCS,
    "IDS": IDS,
    "Greedy": GreedyBestFirst,
    "A*": AStar,
    # "IDA*": IDAStar,  # add when implemented
}

# Mapping for full display names to short names
ALGO_NAME_MAPPING = {
    "DFS (Depth-First Search)": "DFS",
    "BFS (Breadth-First Search)": "BFS",
    "UCS (Uniform Cost Search)": "UCS",
    "Greedy Best-First Search": "Greedy",
    "IDS (Iterative Deepening Search)": "IDS",
    "A* Search": "A*",
    "A*": "A*",
    "Greedy": "Greedy",
    "DFS": "DFS",
    "BFS": "BFS",
    "UCS": "UCS",
    "IDS": "IDS"
}


def normalize_algorithm_name(name: str) -> str:
    """
    Normalize algorithm name to match registry keys.
    Handles both short names (DFS) and full display names (DFS (Depth-First Search)).
    """
    # Try direct lookup in mapping
    if name in ALGO_NAME_MAPPING:
        return ALGO_NAME_MAPPING[name]

    # Try extracting short name from parenthetical format
    # e.g., "DFS (Depth-First Search)" -> "DFS"
    if "(" in name:
        short_name = name.split("(")[0].strip()
        if short_name in ALGO_REGISTRY:
            return short_name

    # Return as-is if no mapping found
    return name


@dataclass
class ComparisonResult:
    """Container for multi-algorithm comparisons that the GUI can display."""
    start: str
    goal: str
    results: List[SearchResult] = field(default_factory=list)

    # Attributes that GUI expects
    optimal_algorithms: List[str] = field(default_factory=list)
    fastest_algorithm: str = ""
    least_expanded_algorithm: str = ""

    def __post_init__(self):
        """Calculate derived attributes after initialization"""
        if self.results:
            self._compute_metrics()

    def _compute_metrics(self):
        """Compute optimal, fastest, and least expanded algorithms"""
        feasible = [r for r in self.results if r.path]

        if not feasible:
            return

        # Find optimal algorithms (those with minimum cost)
        min_cost = min(r.cost for r in feasible)
        self.optimal_algorithms = [r.algorithm_name for r in feasible if r.cost == min_cost]

        # Find fastest algorithm
        fastest = min(feasible, key=lambda r: r.runtime)
        self.fastest_algorithm = fastest.algorithm_name

        # Find algorithm that expanded fewest nodes
        least_expanded = min(feasible, key=lambda r: r.nodes_expanded)
        self.least_expanded_algorithm = least_expanded.algorithm_name

    def best_by_cost(self) -> Optional[SearchResult]:
        """Return the result with the lowest cost"""
        feasible = [r for r in self.results if r.path]
        return min(feasible, key=lambda r: r.cost, default=None)

    def best_by_time(self) -> Optional[SearchResult]:
        """Return the result with the fastest runtime"""
        feasible = [r for r in self.results if r.path]
        return min(feasible, key=lambda r: r.runtime, default=None)


class RoutePlanner:
    def __init__(self, graph: Graph):
        self.graph = graph

    def list_algorithms(self) -> List[str]:
        return list(ALGO_REGISTRY.keys())

    def run_single_algorithm(self, algorithm_name: str, start: str, goal: str) -> SearchResult:
        """Run a single algorithm and return its SearchResult."""
        # Normalize the algorithm name to handle different formats
        normalized_name = normalize_algorithm_name(algorithm_name)

        if normalized_name not in ALGO_REGISTRY:
            raise ValueError(f"Unknown algorithm: {algorithm_name} (normalized to: {normalized_name})")

        algo_cls = ALGO_REGISTRY[normalized_name]
        result = algo_cls(self.graph, start, goal).search()

        # Conservative optimality annotation for the GUI
        if normalized_name in ("UCS", "A*"):
            result.is_optimal = True  # positive weights + admissible heuristic
        else:
            result.is_optimal = False

        return result

    def run_comparison(self, start: str, goal: str, algorithms: List[str], parallel: bool = False) -> ComparisonResult:
        """
        Run multiple algorithms and return a ComparisonResult object.
        If `parallel` is True, algorithms are executed in a small thread pool.
        """
        # Normalize algorithm names before checking registry
        normalized_algos = [normalize_algorithm_name(a) for a in algorithms]
        to_run = [a for a in normalized_algos if a in ALGO_REGISTRY]

        if not to_run:
            raise ValueError("No valid algorithms selected.")

        results: List[SearchResult] = []

        if parallel:
            with ThreadPoolExecutor(max_workers=min(4, len(to_run))) as ex:
                futs = {ex.submit(self.run_single_algorithm, a, start, goal): a for a in to_run}
                for fut in as_completed(futs):
                    results.append(fut.result())
        else:
            for a in to_run:
                results.append(self.run_single_algorithm(a, start, goal))

        order = {name: i for i, name in enumerate(to_run)}
        results.sort(key=lambda r: order.get(r.algorithm_name, 999))

        return ComparisonResult(start=start, goal=goal, results=results)

    def compare_algorithms(self, start: str, goal: str, algorithms: List[str],
                           parallel: bool = False) -> ComparisonResult:
        """Alias for run_comparison to match GUI expectations"""
        return self.run_comparison(start, goal, algorithms, parallel)