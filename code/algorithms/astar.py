from math import inf
from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.search_results import SearchResult
from code.heartofitall.priority_queue import PriorityQueue
from code.utilities.heuristics import haversine_distance


class AStar(SearchAlgorithm):

    # Heuristic function
    # Returns the estimated cost of reaching the goal from the current node
    # h(n) = distance from n to goal
    def _h(self, a: str, b: str) -> float:
        lat1, lon1 = self.graph.get_coordinates(a)
        lat2, lon2 = self.graph.get_coordinates(b)
        return haversine_distance(lat1, lon1, lat2, lon2)

    def search(self) -> SearchResult:
        self._start_timer()

        frontier = PriorityQueue()
        frontier.push(self.start, 0.0)

        came_from = {}
        g = {self.start: 0.0}

        while not frontier.is_empty():
            current = frontier.pop()

            if current == self.goal:
                runtime = self._stop_timer()
                path = self._reconstruct_path(came_from, current)
                return SearchResult(
                    algorithm_name="A*",
                    start=self.start,
                    goal=self.goal,
                    path=path,
                    cost=g[current],
                    nodes_expanded=self.nodes_expanded,
                    runtime=runtime,
                    is_optimal=True
                )

            self.nodes_expanded += 1
            for nbr, w in self.graph.get_neighbors(current).items():
                tentative = g[current] + w
                if tentative < g.get(nbr, inf):
                    g[nbr] = tentative
                    came_from[nbr] = current
                    f = tentative + self._h(nbr, self.goal)
                    frontier.push(nbr, f)

        runtime = self._stop_timer()
        return SearchResult(
            algorithm_name="A*",
            start=self.start,
            goal=self.goal,
            path=[],
            cost=float("inf"),
            nodes_expanded=self.nodes_expanded,
            runtime=runtime,
            is_optimal=False
        )