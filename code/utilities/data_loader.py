# data_loader.py
"""
Data Loader Module (robust)
Handles loading city and edge data from CSV files with flexible headers.
"""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Optional, Dict, Any
import pickle

# Import Graph with a safe fallback so the module works in both package and flat layouts
try:
    from code.heartofitall.graph import Graph
except (ImportError, ModuleNotFoundError):
    # Fallback for when running as flat files
    from code.heartofitall.graph import Graph


def _pick(mapping, *candidates):
    for c in candidates:
        if c in mapping and mapping[c] not in (None, ""):
            return mapping[c]
    return None


def load_graph(cities_file: Path, edges_file: Path, cache_file: Optional[Path] = None) -> Graph:
    """
    Accepts headers:
      Cities:  city|city_name|name , latitude|lat , longitude|lon|lng
      Edges:   city1|source|from , city2|target|to , distance|distance_miles|weight|miles
    """
    if isinstance(cities_file, str):
        cities_file = Path(cities_file)
    if isinstance(edges_file, str):
        edges_file = Path(edges_file)

    # Optional cache
    if cache_file and Path(cache_file).exists():
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass

    g = Graph()

    # --- Cities ---
    with open(cities_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            name = _pick(row, "city", "city_name", "name", "node", "id")
            lat = _pick(row, "latitude", "lat", "y")
            lon = _pick(row, "longitude", "lon", "lng", "x")
            if name is None or lat is None or lon is None:
                raise KeyError("City CSV must contain 'city'/'latitude'/'longitude' (or synonyms). "
                               f"Got headers: {list(row.keys())}")
            g.add_city(name=name, lat=float(lat), lon=float(lon))

    # --- Edges ---
    with open(edges_file, "r", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            a = _pick(row, "city1", "source", "from", "city_a", "a", "source_city")
            b = _pick(row, "city2", "target", "to", "city_b", "b", "dest_city", "destination_city")
            dist = _pick(row, "distance", "weight", "w", "distance_miles", "miles", "length")
            if a is None or b is None or dist is None:
                raise KeyError("Edges CSV must contain 'city1'/'city2'/'distance' (or synonyms). "
                               f"Got headers: {list(row.keys())}")
            g.add_edge(a=a, b=b, distance=float(dist), bidirectional=True)

    # Save cache if requested
    if cache_file:
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(g, f)
        except Exception:
            pass

    return g


def get_graph_statistics(graph: Graph) -> Dict[str, Any]:
    """Return the fields the GUI expects."""
    total_cities = len(graph.cities)
    undirected_edges = set()
    distances = []
    total_road_miles = 0.0
    for a, neighbors in graph.adjacency.items():
        for b, d in neighbors.items():
            key = tuple(sorted((a, b)))
            if key in undirected_edges:
                continue
            undirected_edges.add(key)
            total_road_miles += d
            distances.append(d)

    total_edges = len(undirected_edges)
    average_degree = (2 * total_edges / total_cities) if total_cities else 0.0
    if distances:
        min_distance = min(distances)
        max_distance = max(distances)
        avg_distance = sum(distances) / len(distances)
    else:
        min_distance = max_distance = avg_distance = 0.0

    return {
        "total_cities": total_cities,
        "total_edges": total_edges,
        "average_degree": average_degree,
        "total_road_miles": total_road_miles,
        "min_distance": min_distance,
        "max_distance": max_distance,
        "avg_distance": avg_distance,
    }