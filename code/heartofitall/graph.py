from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class City:
    name: str
    latitude: float
    longitude: float

class Graph:
    def __init__(self) -> None:
        self.cities: Dict[str, City] = {}
        # adjacency[u][v] = distance (miles)
        self.adjacency: Dict[str, Dict[str, float]] = defaultdict(dict)

    # city / edge management
    def add_city(self, name: str, lat: float, lon: float) -> None:
        self.cities[name] = City(name, float(lat), float(lon))

    def add_edge(self, a: str, b: str, distance: float, bidirectional: bool = True) -> None:
        d = float(distance)
        self.adjacency[a][b] = d
        if bidirectional:
            self.adjacency[b][a] = d

    # queries used by algs
    def get_neighbors(self, city: str) -> Dict[str, float]:
        return self.adjacency.get(city, {})

    def get_distance(self, a: str, b: str) -> float:
        return self.adjacency[a][b]

    def get_all_cities(self) -> List[str]:
        return list(self.cities.keys())

    def get_coordinates(self, city: str) -> Tuple[float, float]:
        c = self.cities[city]
        return (c.latitude, c.longitude)
