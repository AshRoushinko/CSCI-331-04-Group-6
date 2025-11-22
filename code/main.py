from pathlib import Path

from pathlib import Path
from utilities.data_loader import load_graph
from algorithms.bfs import BFS
from algorithms.dfs import DFS
from algorithms.ucs import UCS
from algorithms.greedy import GreedyBestFirst
from algorithms.astar import AStar
from algorithms.ids import IDS

ALGOS = {
    "DFS": DFS,
    "BFS": BFS,
    "UCS": UCS,
    "Greedy": GreedyBestFirst,
    "A*": AStar,
    "IDS": IDS,
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
        results.append(str(res))
    return results

if __name__ == "__main__":
    # Get the project root directory (parent of 'code' directory)
    run_compare("Rochester", "Yonkers")
