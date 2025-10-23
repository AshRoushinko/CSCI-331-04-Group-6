from pathlib import Path

from pathlib import Path
from code.utilities.data_loader import load_graph
from code.algorithms.bfs import BFS
from code.algorithms.ucs import UCS
from code.algorithms.greedy import GreedyBestFirst
from code.algorithms.astar import AStar

ALGOS = {
    "BFS": BFS,
    "UCS": UCS,
    "Greedy": GreedyBestFirst,
    "A*": AStar,
    "BFS": BFS,
    # "IDS": IDS,
    # "IDA*": IDAStar,
}


def run_compare(start: str, goal: str):
    project_root = Path(__file__).parent.parent
    cities_csv = project_root / "data" / "cities.csv"
    edges_csv = project_root / "data" / "edges.csv"
    g = load_graph(cities_csv, edges_csv)
    results = []
    for name, cls in ALGOS.items():
        res = cls(g, start, goal).search()
        print(res)
        results.append(res)
    return results

if __name__ == "__main__":
    # Get the project root directory (parent of 'code' directory)
    run_compare("Rochester", "New York City")
