"""
Data Loader Module
Handles loading city and edge data from CSV files
"""

import csv
from pathlib import Path
from typing import Optional
import pickle

from code.heartofitall.graph import Graph


def load_graph(cities_file: Path, edges_file: Path,
               cache_file: Optional[Path] = None) -> Graph:
    """
    Load graph from CSV files

    Args:
        cities_file: Path to cities.csv
        edges_file: Path to edges.csv
        cache_file: Optional path to cache the loaded graph

    Returns:
        Graph object with cities and edges loaded
    """
    # Try to load from cache if available
    if cache_file and cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Failed to load cache: {e}")

    graph = Graph()

    # Load cities
    with open(cities_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            graph.add_city(
                name=row['city'].strip(),
                lat=float(row['latitude']),
                lon=float(row['longitude'])
            )

    # Load edges
    with open(edges_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            graph.add_edge(
                a=row['city1'].strip(),
                b=row['city2'].strip(),
                distance=float(row['distance']),
                bidirectional=True  # Assume all roads are bidirectional
            )

    # Cache the graph if cache_file is provided
    if cache_file:
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(graph, f)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    return graph


def validate_graph_data(graph: Graph) -> dict:
    """
    Validate the loaded graph data

    Returns:
        Dictionary with validation results
    """
    results = {
        'city_count': len(graph.cities),
        'edge_count': sum(len(neighbors) for neighbors in graph.adjacency.values()) // 2,
        'connected_components': 0,
        'isolated_cities': [],
        'missing_coordinates': [],
        'invalid_edges': []
    }

    # Check for isolated cities (no edges)
    for city in graph.cities:
        if city not in graph.adjacency or not graph.adjacency[city]:
            results['isolated_cities'].append(city)

    # Check for missing coordinates
    for city_name, city in graph.cities.items():
        if city.latitude == 0 and city.longitude == 0:
            results['missing_coordinates'].append(city_name)

    # Validate edges (ensure both cities exist)
    for city_a, neighbors in graph.adjacency.items():
        if city_a not in graph.cities:
            results['invalid_edges'].append(f"{city_a} not in cities list")
        for city_b in neighbors:
            if city_b not in graph.cities:
                results['invalid_edges'].append(f"{city_b} not in cities list")

    return results


def get_graph_statistics(graph: Graph) -> dict:
    """
    Get statistics about the graph

    Returns:
        Dictionary with graph statistics
    """
    all_distances = []
    for city_a, neighbors in graph.adjacency.items():
        for city_b, distance in neighbors.items():
            if city_a < city_b:  # Avoid counting edges twice
                all_distances.append(distance)

    stats = {
        'total_cities': len(graph.cities),
        'total_edges': len(all_distances),
        'average_degree': sum(len(neighbors) for neighbors in graph.adjacency.values()) / len(
            graph.cities) if graph.cities else 0,
        'min_distance': min(all_distances) if all_distances else 0,
        'max_distance': max(all_distances) if all_distances else 0,
        'avg_distance': sum(all_distances) / len(all_distances) if all_distances else 0,
        'total_road_miles': sum(all_distances)
    }

    return stats


def export_graph_to_csv(graph: Graph, cities_output: Path, edges_output: Path):
    """
    Export graph back to CSV format

    Args:
        graph: Graph object to export
        cities_output: Path for cities CSV output
        edges_output: Path for edges CSV output
    """
    # Export cities
    with open(cities_output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['city', 'latitude', 'longitude'])
        writer.writeheader()
        for city_name, city in graph.cities.items():
            writer.writerow({
                'city': city_name,
                'latitude': city.latitude,
                'longitude': city.longitude
            })

    # Export edges (avoid duplicates)
    exported = set()
    with open(edges_output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['city1', 'city2', 'distance'])
        writer.writeheader()
        for city_a, neighbors in graph.adjacency.items():
            for city_b, distance in neighbors.items():
                edge = tuple(sorted([city_a, city_b]))
                if edge not in exported:
                    writer.writerow({
                        'city1': city_a,
                        'city2': city_b,
                        'distance': distance
                    })
                    exported.add(edge)