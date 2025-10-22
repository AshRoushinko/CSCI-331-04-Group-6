#template for search alg implementation

from __future__ import annotations
from abc import ABC, abstractmethod
import time
from typing import Dict, List
from code.heartofitall.graph import Graph
from code.heartofitall.search_results import SearchResult


# constructor
class SearchAlgorithm(ABC):
    def __init__(self, graph: Graph, start: str, goal: str) -> None:
        self.graph = graph
        self.start = start
        self.goal = goal
        self.nodes_expanded = 0
        self._t0 = 0.0

    def _start_timer(self): self._t0 = time.perf_counter()
    def _stop_timer(self) -> float: return time.perf_counter() - self._t0

    #came_from is a dictionary mapping each node to its parent
    #current is the the goal node which will be used to backtrack
    # builds path in reverse by following parenent pointer
    # reverses the list to get the true path

    def _reconstruct_path(self, came_from: Dict[str, str], current: str) -> List[str]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


    # to be implemented by all subclass search algs
    #returns a search result object containing the path found and total cost
    @abstractmethod
    def search(self) -> SearchResult:
        ...
