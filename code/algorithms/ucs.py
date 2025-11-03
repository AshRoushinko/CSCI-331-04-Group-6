from typing import Dict
from math import inf
from algorithms.base_algorithm import SearchAlgorithm
from heartofitall.search_results import SearchResult
from heartofitall.priority_queue import PriorityQueue

class UCS(SearchAlgorithm):

    def search(self) -> SearchResult:
        self._start_timer()

        #initialization
        frontier = PriorityQueue() # priority queue that orders nodes by their path cost
        frontier.push(self.start, 0.0)

        came_from: Dict[str, str] = {} # tracks the parent of each node to reconstruct the path later
        cost_so_far: Dict[str, float] = {self.start: 0.0} # stores the cheapest known cost to reach each node



        while not frontier.is_empty():
            current = frontier.pop()
            current_cost = cost_so_far[current]

            # Goal test when a node is selected for expansion ( not when discovered )
            if current == self.goal:
                runtime = self._stop_timer()
                path = self._reconstruct_path(came_from, current)
                return SearchResult(
                    path=path,
                    cost=current_cost,
                    nodes_expanded=self.nodes_expanded,
                    runtime=runtime,
                    is_optimal=True,      # Non-negative road distances => optimal
                    algorithm_name="UCS"
                )


            # Expand current
            # Pops the lowest-cost node
            # Checks if it's the goal
            self.nodes_expanded += 1
            for neighbor, edge_dist in self.graph.get_neighbors(current).items():
                new_cost = current_cost + edge_dist
                # Only improve if strictly better path found
                if new_cost < cost_so_far.get(neighbor, inf):
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    frontier.push(neighbor, new_cost)

        # If we exhaust the frontier, goal is unreachable
        runtime = self._stop_timer()
        return SearchResult(
            path=[],
            cost=inf,
            nodes_expanded=self.nodes_expanded,
            runtime=runtime,
            is_optimal=False,
            algorithm_name="UCS"
        )
