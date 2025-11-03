from collections import deque
from typing import Dict, Set
from algorithms.base_algorithm import SearchAlgorithm
from heartofitall.search_results import SearchResult

# roc -> bat -> buf-> james -> corn -> ~~ith~~ ->  

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
        #visited = set()

        # while frontier:
        #     u = frontier.pop()
        #     if u == self.goal:
        #         break
        #     print('current node: ', u)
        #     visited.add(u)
        #     print("Visited: ", visited)


        #     self.nodes_expanded += 1
        #     for v, _dist in self.graph.get_neighbors(u).items():
        #         if v not in visited:
        #             came_from[v] = u
        #             frontier.append(v)
        #     print("Frontier: ", frontier)

        runtime = self._stop_timer()
        if self.goal not in came_from and self.goal != self.start:
            return SearchResult([], float("inf"), self.nodes_expanded, runtime, False, "DFS")
        path = [self.start] if self.start == self.goal else self._reconstruct_path(came_from, self.goal)
        # DFS path cost = sum of road distances along path
        #path_cost = sum(self.graph.get_edge_data(u, v)["weight"] for u, v in zip(path[:-1], path[1:]))
        cost = 0.0
        for a, b in zip(path, path[1:]):
            cost += self.graph.get_distance(a, b)
        return SearchResult(path, cost, self.nodes_expanded, runtime, True, "DFS")