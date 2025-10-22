from pathlib import Path
from utilities.data_loader import load_graph
from algorithms.ucs import UCS

if __name__ == "__main__":
    g = load_graph(Path("data/cities.csv"), Path("data/edges.csv"))
    algo = UCS(g, start="Rochester", goal="Buffalo")
    result = algo.search()
    print(result)
