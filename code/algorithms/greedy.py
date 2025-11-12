from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.search_results import SearchResult
from code.heartofitall.priority_queue import PriorityQueue
from code.utilities.heuristics import haversine_distance


class GreedyBestFirst(SearchAlgorithm):

    # Heuristic function
    # Returns the estimated cost of reaching the goal from the current node
    # h(n) = distance from n to goal
    def _h(self, node: str) -> float:
        lat1, lon1 = self.graph.get_coordinates(node)
        lat2, lon2 = self.graph.get_coordinates(self.goal)
        return haversine_distance(lat1, lon1, lat2, lon2)

    def search(self) -> SearchResult:
        self._start_timer()

        # Creates a priority queue ordered by heuristic values
        frontier = PriorityQueue()
        frontier.push(self.start, self._h(self.start))

        came_from = {}
        visited = {self.start}

        while not frontier.is_empty():
            current = frontier.pop()

            if current == self.goal:
                runtime = self._stop_timer()
                path = self._reconstruct_path(came_from, current)
                cost = sum(self.graph.get_distance(a, b) for a, b in zip(path, path[1:]))
                return SearchResult(
                    algorithm_name="Greedy",
                    start=self.start,
                    goal=self.goal,
                    path=path,
                    cost=cost,
                    nodes_expanded=self.nodes_expanded,
                    runtime=runtime,
                    is_optimal=False
                )

            self.nodes_expanded += 1
            for nbr, _ in self.graph.get_neighbors(current).items():
                if nbr not in visited:
                    visited.add(nbr)
                    came_from[nbr] = current
                    frontier.push(nbr, self._h(nbr))

        runtime = self._stop_timer()
        return SearchResult(
            algorithm_name="Greedy",
            start=self.start,
            goal=self.goal,
            path=[],
            cost=float("inf"),
            nodes_expanded=self.nodes_expanded,
            runtime=runtime,
            is_optimal=False
        )