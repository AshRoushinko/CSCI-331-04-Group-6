#!/usr/bin/env python3
"""
Diagnostic script to identify issues with the route planner
Run this from your project root: python3 diagnostic_test_improved.py
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print("=" * 60)
print("DIAGNOSTIC TEST FOR ROUTE PLANNER")
print("=" * 60)
print(f"\nProject root: {ROOT}")
print(f"Python path: {sys.path[:3]}...")

# Test 0: Check project structure
print("\n[TEST 0] Checking project structure...")
required_files = [
    "code/utilities/data_loader.py",
    "code/utilities/route_planner.py",
    "code/heartofitall/graph.py",
    "code/heartofitall/search_results.py",
    "code/algorithms/bfs.py",
]

# Check for CSV files in multiple possible locations
csv_locations = [
    ("data/cities.csv", "data/edges.csv"),
    ("cities.csv", "edges.csv"),
]

cities_file = None
edges_file = None

for cities_path, edges_path in csv_locations:
    cities_full = ROOT / cities_path
    edges_full = ROOT / edges_path
    if cities_full.exists() and edges_full.exists():
        cities_file = cities_full
        edges_file = edges_full
        required_files.append(cities_path)
        required_files.append(edges_path)
        break

missing_files = []
for f in required_files:
    path = ROOT / f
    if path.exists():
        print(f"  ✓ {f}")
    else:
        print(f"  ✗ {f} NOT FOUND")
        missing_files.append(f)

if cities_file is None or edges_file is None:
    print(f"\n✗ Could not find cities.csv and edges.csv")
    print(f"  Checked locations:")
    for cities_path, edges_path in csv_locations:
        print(f"    - {cities_path} and {edges_path}")
    sys.exit(1)

print(f"\n  Using CSV files:")
print(f"    Cities: {cities_file.relative_to(ROOT)}")
print(f"    Edges:  {edges_file.relative_to(ROOT)}")

if missing_files:
    print(f"\n✗ Missing {len(missing_files)} required files. Cannot continue.")
    sys.exit(1)

# Test 1: Import modules
print("\n[TEST 1] Testing imports...")
try:
    from code.utilities.data_loader import load_graph, get_graph_statistics

    print("✓ data_loader imported successfully")
except Exception as e:
    print(f"✗ data_loader import failed: {e}")
    print("\nTrying to debug the import issue...")
    print(f"Does code/__init__.py exist? {(ROOT / 'code' / '__init__.py').exists()}")
    print(f"Does code/utilities/__init__.py exist? {(ROOT / 'code' / 'utilities' / '__init__.py').exists()}")

    import traceback

    traceback.print_exc()
    sys.exit(1)

try:
    from code.utilities.route_planner import RoutePlanner

    print("✓ RoutePlanner imported successfully")
except Exception as e:
    print(f"✗ RoutePlanner import failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

try:
    from code.heartofitall.graph import Graph

    print("✓ Graph imported successfully")
except Exception as e:
    print(f"✗ Graph import failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

try:
    from code.heartofitall.search_results import SearchResult

    print("✓ SearchResult imported successfully")
except Exception as e:
    print(f"✗ SearchResult import failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 2: Load graph
print("\n[TEST 2] Loading graph data...")
try:
    graph = load_graph(cities_file, edges_file)
    print(f"✓ Graph loaded: {len(graph.cities)} cities, {len(graph.adjacency)} nodes")

    # Show some cities
    cities = list(graph.cities.keys())[:5]
    print(f"  Sample cities: {', '.join(cities)}")

except Exception as e:
    print(f"✗ Graph loading failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 3: Create RoutePlanner
print("\n[TEST 3] Creating RoutePlanner...")
try:
    route_planner = RoutePlanner(graph)
    print(f"✓ RoutePlanner created")
    print(f"  Type: {type(route_planner)}")
    print(f"  Has run_single_algorithm: {hasattr(route_planner, 'run_single_algorithm')}")

    # Check what run_single_algorithm is
    if hasattr(route_planner, 'run_single_algorithm'):
        method = getattr(route_planner, 'run_single_algorithm')
        print(f"  run_single_algorithm type: {type(method)}")
        print(f"  Is callable: {callable(method)}")
except Exception as e:
    print(f"✗ RoutePlanner creation failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Run a simple algorithm
print("\n[TEST 4] Testing algorithm execution...")
try:
    # Get some test cities
    cities = list(graph.cities.keys())
    if len(cities) < 2:
        print("✗ Not enough cities in graph")
        sys.exit(1)

    start = cities[0]
    goal = cities[1]
    print(f"  Testing route from {start} to {goal}")

    # Try to run BFS
    print(f"  Calling route_planner.run_single_algorithm('BFS', '{start}', '{goal}')...")
    result = route_planner.run_single_algorithm('BFS', start, goal)

    print(f"✓ Algorithm executed successfully")
    print(f"  Result type: {type(result)}")

    # Check expected attributes
    expected_attrs = ['algorithm_name', 'start', 'goal', 'path', 'cost', 'nodes_expanded', 'runtime', 'is_optimal']
    missing_attrs = []
    for attr in expected_attrs:
        has_it = hasattr(result, attr)
        symbol = "✓" if has_it else "✗"
        print(f"  {symbol} Has '{attr}': {has_it}")
        if has_it:
            value = getattr(result, attr)
            if attr in ['path']:
                print(f"      Value: {value}")
            else:
                print(f"      Value: {value} (type: {type(value).__name__})")
        else:
            missing_attrs.append(attr)

    if missing_attrs:
        print(f"\n✗ Missing attributes: {missing_attrs}")
        print("You need to update your SearchResult class and algorithm files!")
        sys.exit(1)

except Exception as e:
    print(f"✗ Algorithm execution failed: {e}")
    import traceback

    traceback.print_exc()

    # Additional debugging
    print("\n[DEBUG] Checking route_planner attributes:")
    for attr in dir(route_planner):
        if not attr.startswith('_'):
            val = getattr(route_planner, attr)
            print(f"  {attr}: {type(val)}")
    sys.exit(1)

# Test 5: Test comparison
print("\n[TEST 5] Testing algorithm comparison...")
try:
    comparison_result = route_planner.compare_algorithms(
        start=cities[0],
        goal=cities[1],
        algorithms=['BFS', 'DFS']
    )
    print(f"✓ Comparison executed successfully")
    print(f"  Result type: {type(comparison_result)}")

    # Check for required attributes
    required_attrs = ['optimal_algorithms', 'fastest_algorithm', 'least_expanded_algorithm', 'results']
    missing_attrs = []

    for attr in required_attrs:
        has_it = hasattr(comparison_result, attr)
        symbol = "✓" if has_it else "✗"
        if has_it:
            val = getattr(comparison_result, attr)
            print(f"  {symbol} Has '{attr}': {val}")
        else:
            print(f"  {symbol} Missing '{attr}'")
            missing_attrs.append(attr)

    if missing_attrs:
        print(f"\n✗ Missing attributes in ComparisonResult: {missing_attrs}")
        print("You need to update your route_planner.py!")
        sys.exit(1)

except Exception as e:
    print(f"✗ Comparison failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓✓✓ ALL TESTS PASSED ✓✓✓")
print("=" * 60)
print("\nYour route planner is ready! You can now run the GUI:")
print("  python3 -m code.gui.gui_app")
print("=" * 60)