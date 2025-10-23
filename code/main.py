from pathlib import Path
from utilities.data_loader import load_graph
from algorithms.ucs import UCS

if __name__ == "__main__":
    # Get the project root directory (parent of 'code' directory)
    project_root = Path(__file__).parent.parent

    # Build paths relative to project root
    cities_csv = project_root / "data" / "cities.csv"
    edges_csv = project_root / "data" / "edges.csv"

    g = load_graph(cities_csv, edges_csv)
    algo = UCS(g, start="Rochester", goal="Jamestown")
    result = algo.search()
    print(result)