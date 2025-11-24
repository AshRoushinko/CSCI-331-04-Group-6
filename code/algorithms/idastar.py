from math import inf
from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.search_results import SearchResult
from code.utilities.heuristics import haversine_distance


class IDAStar(SearchAlgorithm):

    def _h(self, node: str) -> float:
        """Heuristic: haversine distance from node to goal."""
        lat1, lon1 = self.graph.get_coordinates(node)
        lat2, lon2 = self.graph.get_coordinates(self.goal)
        return haversine_distance(lat1, lon1, lat2, lon2)

    def search(self) -> SearchResult:
        self._start_timer()

        threshold = self._h(self.start)

        path = [self.start]
        g_costs = [0.0]

        while True:
            result = self._bounded_search(path, g_costs, threshold)

            if isinstance(result, list):
                runtime = self._stop_timer()
                cost = g_costs[-1]
                return SearchResult(
                    algorithm_name="IDA*",
                    start=self.start,
                    goal=self.goal,
                    path=result,
                    cost=cost,
                    nodes_expanded=self.nodes_expanded,
                    runtime=runtime,
                    is_optimal=True
                )

            if result == inf:
                runtime = self._stop_timer()
                return SearchResult(
                    algorithm_name="IDA*",
                    start=self.start,
                    goal=self.goal,
                    path=[],
                    cost=inf,
                    nodes_expanded=self.nodes_expanded,
                    runtime=runtime,
                    is_optimal=False
                )

            threshold = result

    def _bounded_search(self, path: list, g_costs: list, threshold: float):
        """
        Recursive depth-first search bounded by f-cost threshold.

        Returns:
            - The path (list) if goal is found
            - inf if no solution exists
            - The minimum f-cost exceeding threshold (for next iteration)
        """
        node = path[-1]
        g = g_costs[-1]
        f = g + self._h(node)

        if f > threshold:
            return f

        if node == self.goal:
            return list(path)

        self.nodes_expanded += 1
        min_exceeded = inf

        for neighbor, edge_cost in self.graph.get_neighbors(node).items():
            if neighbor not in path:
                path.append(neighbor)
                g_costs.append(g + edge_cost)

                result = self._bounded_search(path, g_costs, threshold)

                if isinstance(result, list):
                    return result

                if result < min_exceeded:
                    min_exceeded = result

                path.pop()
                g_costs.pop()

        return min_exceeded