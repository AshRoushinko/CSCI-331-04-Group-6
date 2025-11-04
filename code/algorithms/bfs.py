from collections import deque
from typing import Dict, Set
from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.search_results import SearchResult

class BFS(SearchAlgorithm):
    def search(self) -> SearchResult:
        self._start_timer()
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

        runtime = self._stop_timer()
        if self.goal not in came_from and self.goal != self.start:
            return SearchResult([], float("inf"), self.nodes_expanded, runtime, False, "BFS")

        path = [self.start] if self.start == self.goal else self._reconstruct_path(came_from, self.goal)
        # BFS path cost = sum of road distances along path
        cost = 0.0
        for a, b in zip(path, path[1:]):
            cost += self.graph.get_distance(a, b)
        return SearchResult(path, cost, self.nodes_expanded, runtime, False, "BFS")
