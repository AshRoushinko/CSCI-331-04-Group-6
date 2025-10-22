# I hardly know her!

import csv
from pathlib import Path
from typing import Iterable
from ..heartofitall.graph import Graph


# cleans up white space from strings if need be
def _clean(s: str) -> str:
    return s.strip()

def load_graph(cities_csv: Path, edges_csv: Path) -> Graph:
    g = Graph()

    #  load cities
    with open(cities_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip city_name, latitude, and longitude
        for row in reader:
            if not row or len(row) < 3:
                continue
            name = _clean(row[0])
            try:
                lat = float(_clean(row[1]))
                lon = float(_clean(row[2]))
            except ValueError:
                # skip rows if the data is messed up
                continue
            g.add_city(name, lat, lon)

    # load edges
    with open(edges_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)   # skip  city1, city2, distance_miles
        for row in reader:
            if not row or len(row) < 3:
                continue
            a, b = _clean(row[0]), _clean(row[1])
            try:
                d = float(_clean(row[2]))
            except ValueError:
                continue
            if a in g.cities and b in g.cities:
                g.add_edge(a, b, d, bidirectional=True)
            # else: quietly ignore or log a warning

    return g
