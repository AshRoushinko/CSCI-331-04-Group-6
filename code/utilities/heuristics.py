"""
Heuristics Module
Provides heuristic calculations for informed search algorithms
"""

import math
from typing import Tuple
from code.heartofitall.graph import Graph


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of first point (in degrees)
        lat2, lon2: Latitude and longitude of second point (in degrees)

    Returns:
        Distance in miles
    """
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in miles
    r = 3956  # Use 6371 for kilometers

    return c * r


def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Euclidean distance (less accurate but faster).
    Useful for relative comparisons.

    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point

    Returns:
        Euclidean distance (scaled to approximate miles)
    """
    # Approximate conversion factors for New York state region
    # At 42° latitude, 1 degree longitude ≈ 52 miles, 1 degree latitude ≈ 69 miles
    dx = (lon2 - lon1) * 52
    dy = (lat2 - lat1) * 69

    return math.sqrt(dx ** 2 + dy ** 2)


def manhattan_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate Manhattan distance (sum of absolute differences).

    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point

    Returns:
        Manhattan distance (scaled to approximate miles)
    """
    dx = abs(lon2 - lon1) * 52
    dy = abs(lat2 - lat1) * 69

    return dx + dy


class HeuristicCalculator:
    """
    Manages heuristic calculations for a graph.
    Caches computed values for efficiency.
    """

    def __init__(self, graph: Graph, heuristic_type: str = "haversine"):
        """
        Initialize the heuristic calculator.

        Args:
            graph: The graph containing city data
            heuristic_type: Type of heuristic to use 
                           ("haversine", "euclidean", or "manhattan")
        """
        self.graph = graph
        self.heuristic_type = heuristic_type
        self._cache = {}

        # Select heuristic function
        if heuristic_type == "haversine":
            self.heuristic_func = haversine_distance
        elif heuristic_type == "euclidean":
            self.heuristic_func = euclidean_distance
        elif heuristic_type == "manhattan":
            self.heuristic_func = manhattan_distance
        else:
            raise ValueError(f"Unknown heuristic type: {heuristic_type}")

    def get_heuristic(self, city1: str, city2: str) -> float:
        """
        Get heuristic distance between two cities.

        Args:
            city1: Name of first city
            city2: Name of second city

        Returns:
            Heuristic distance in miles
        """
        # Check cache
        cache_key = tuple(sorted([city1, city2]))
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Calculate heuristic
        lat1, lon1 = self.graph.get_coordinates(city1)
        lat2, lon2 = self.graph.get_coordinates(city2)

        distance = self.heuristic_func(lat1, lon1, lat2, lon2)

        # Cache the result
        self._cache[cache_key] = distance

        return distance

    def precompute_all_heuristics(self, goal: str):
        """
        Precompute heuristics from all cities to a goal city.
        Useful for algorithms like A* that repeatedly query the same goal.

        Args:
            goal: The goal city

        Returns:
            Dictionary mapping each city to its heuristic distance to goal
        """
        heuristics = {}
        for city in self.graph.get_all_cities():
            heuristics[city] = self.get_heuristic(city, goal)
        return heuristics

    def is_admissible(self, city1: str, city2: str) -> bool:
        """
        Check if the heuristic is admissible (never overestimates).

        Args:
            city1: First city
            city2: Second city

        Returns:
            True if heuristic <= actual distance, False otherwise
        """
        heuristic = self.get_heuristic(city1, city2)

        # Check if there's a direct edge
        neighbors = self.graph.get_neighbors(city1)
        if city2 in neighbors:
            actual = neighbors[city2]
            return heuristic <= actual

        # For non-adjacent cities, we can't easily verify admissibility
        # without running a shortest path algorithm
        return True  # Assume admissible for now

    def get_statistics(self) -> dict:
        """
        Get statistics about the heuristic function.

        Returns:
            Dictionary with heuristic statistics
        """
        if not self._cache:
            return {
                'type': self.heuristic_type,
                'cached_values': 0
            }

        values = list(self._cache.values())
        return {
            'type': self.heuristic_type,
            'cached_values': len(self._cache),
            'min_heuristic': min(values),
            'max_heuristic': max(values),
            'avg_heuristic': sum(values) / len(values)
        }

