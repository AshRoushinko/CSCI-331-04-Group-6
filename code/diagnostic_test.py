#!/usr/bin/env python3
"""
Diagnostic script to identify the 'str' object is not callable error
Run this from your project root: python3 diagnostic_test.py
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

# Test 1: Import modules
print("\n[TEST 1] Testing imports...")
try:
    from code.utilities.data_loader import load_graph, get_graph_statistics

    print("✓ data_loader imported successfully")
except Exception as e:
    print(f"✗ data_loader import failed: {e}")
    sys.exit(1)

try:
    from code.utilities.route_planner import RoutePlanner

    print("✓ RoutePlanner imported successfully")
except Exception as e:
    print(f"✗ RoutePlanner import failed: {e}")
    sys.exit(1)

try:
    from code.heartofitall.graph import Graph

    print("✓ Graph imported successfully")
except Exception as e:
    print(f"✗ Graph import failed: {e}")
    sys.exit(1)

# Test 2: Load graph
print("\n[TEST 2] Loading graph data...")
try:
    cities_file = Path("cities.csv")
    edges_file = Path("edges.csv")

    if not cities_file.exists():
        print(f"✗ cities.csv not found at {cities_file.absolute()}")
        sys.exit(1)
    if not edges_file.exists():
        print(f"✗ edges.csv not found at {edges_file.absolute()}")
        sys.exit(1)

    graph = load_graph(cities_file, edges_file)
    print(f"✓ Graph loaded: {len(graph.cities)} cities, {len(graph.adjacency)} nodes")
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
    print(f"  Result attributes: {dir(result)}")

    # Check expected attributes
    expected_attrs = ['algorithm_name', 'path', 'cost', 'nodes_expanded', 'runtime', 'is_optimal']
    for attr in expected_attrs:
        has_it = hasattr(result, attr)
        symbol = "✓" if has_it else "✗"
        print(f"  {symbol} Has '{attr}': {has_it}")
        if has_it:
            value = getattr(result, attr)
            print(f"      Value: {value} (type: {type(value).__name__})")

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
    print(f"  Result attributes: {[a for a in dir(comparison_result) if not a.startswith('_')]}")

    # Check for optimal_algorithms
    if hasattr(comparison_result, 'optimal_algorithms'):
        print(f"  ✓ Has 'optimal_algorithms': {comparison_result.optimal_algorithms}")
    else:
        print(f"  ✗ Missing 'optimal_algorithms' attribute")
        print(f"  Available attributes: {vars(comparison_result)}")

except Exception as e:
    print(f"✗ Comparison failed: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)