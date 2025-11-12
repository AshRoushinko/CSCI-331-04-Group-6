from collections import deque
from typing import Dict, Set
from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.graph import Graph
from code.heartofitall.search_results import SearchResult


class DFS(SearchAlgorithm):
    def helper(self, node: str, visited: Set[str], came_from: Dict[str, str]) -> bool:
        if node == self.goal:
            return True
        visited.add(node)
        self.nodes_expanded += 1
        for neighbor, _dist in self.graph.get_neighbors(node).items():
            if neighbor not in visited:
                came_from[neighbor] = node
                if self.helper(neighbor, visited, came_from):
                    return True
        return False

    def search(self) -> SearchResult:
        self._start_timer()
        came_from: Dict[str, str] = {}
        visited: Set[str] = set()
        self.helper(self.start, visited, came_from)

        runtime = self._stop_timer()

        # Check if goal was reached
        if self.goal not in came_from and self.goal != self.start:
            return SearchResult(
                algorithm_name="DFS",
                start=self.start,
                goal=self.goal,
                path=[],
                cost=float("inf"),
                nodes_expanded=self.nodes_expanded,
                runtime=runtime,
                is_optimal=False
            )

        # Reconstruct path
        path = [self.start] if self.start == self.goal else self._reconstruct_path(came_from, self.goal)

        # Calculate path cost
        cost = 0.0
        for a, b in zip(path, path[1:]):
            cost += self.graph.get_distance(a, b)

        return SearchResult(
            algorithm_name="DFS",
            start=self.start,
            goal=self.goal,
            path=path,
            cost=cost,
            nodes_expanded=self.nodes_expanded,
            runtime=runtime,
            is_optimal=False
        )