from collections import deque
from typing import Dict, Set
import time
from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.graph import Graph
from code.heartofitall.search_results import SearchResult


class BFS:
    def __init__(self, graph: Graph, start: str, goal: str):
        self.graph = graph
        self.start = start
        self.goal = goal
        self.nodes_expanded = 0

    def search(self) -> SearchResult:
        start_time = time.time()

        frontier = deque([self.start])
        came_from: Dict[str, str] = {}
        visited: Set[str] = {self.start}

        while frontier:
            u = frontier.popleft()
            if u == self.goal:
                break
            self.nodes_expanded += 1
            for v, _dist in self.graph.get_neighbors(u).items():
                if v not in visited:
                    visited.add(v)
                    came_from[v] = u
                    frontier.append(v)

        runtime = time.time() - start_time

        if self.goal not in came_from and self.goal != self.start:
            return SearchResult(
                algorithm_name="BFS",
                start=self.start,
                goal=self.goal,
                path=[],
                cost=float("inf"),
                nodes_expanded=self.nodes_expanded,
                runtime=runtime,
                is_optimal=False
            )

        path = [self.start] if self.start == self.goal else self._reconstruct_path(came_from, self.goal)

        # BFS path cost = sum of road distances along path
        cost = 0.0
        for a, b in zip(path, path[1:]):
            cost += self.graph.get_distance(a, b)

        return SearchResult(
            algorithm_name="BFS",
            start=self.start,
            goal=self.goal,
            path=path,
            cost=cost,
            nodes_expanded=self.nodes_expanded,
            runtime=runtime,
            is_optimal=False
        )

    def _reconstruct_path(self, came_from: Dict[str, str], goal: str) -> list:
        """Reconstruct the path from start to goal"""
        path = []
        current = goal
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(self.start)
        return path[::-1]