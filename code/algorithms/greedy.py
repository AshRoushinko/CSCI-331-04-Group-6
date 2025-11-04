from code.algorithms.base_algorithm import SearchAlgorithm
from code.heartofitall.search_results import SearchResult
from code.heartofitall.priority_queue import PriorityQueue
from code.utilities.heuristics import haversine_distance

class GreedyBestFirst(SearchAlgorithm):

    # heuristic function
    # returns the estimated cost of reaching the goal from the current node
    # h(n) = distance from n to goal
    def _h(self, node: str) -> float:
        lat1, lon1 = self.graph.get_coordinates(node)
        lat2, lon2 = self.graph.get_coordinates(self.goal)
        return haversine_distance(lat1, lon1, lat2, lon2)

    # Creates a priority queue ordered by heuristic values frontier
    # frontier is a priority queue that orders nodes by their path cost
    # came_from is a dictionary mapping each node to its parent
    # current is the the goal node which will be used to backtrack
    # builds path in reverse by following parenent pointer
    # reverses the list to get the true path

    def search(self) -> SearchResult:
        self._start_timer()
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
                return SearchResult(path, cost, self.nodes_expanded, runtime, False, "Greedy")

            self.nodes_expanded += 1
            for nbr, _ in self.graph.get_neighbors(current).items():
                if nbr not in visited:
                    visited.add(nbr)
                    came_from[nbr] = current
                    frontier.push(nbr, self._h(nbr))

        runtime = self._stop_timer()
        return SearchResult([], float("inf"), self.nodes_expanded, runtime, False, "Greedy")
