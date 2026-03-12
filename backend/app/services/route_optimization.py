from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Iterable, List, Tuple

import networkx as nx


@dataclass
class BinNode:
    id: str
    lat: float
    lng: float
    fill_level_pct: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points on Earth in kilometers.
    """
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def build_graph(bins: Iterable[BinNode]) -> nx.Graph:
    """
    Build a fully connected weighted graph of bins using haversine distance as edge weight.
    """
    g = nx.Graph()
    nodes = list(bins)
    for b in nodes:
        g.add_node(b.id, lat=b.lat, lng=b.lng, fill=b.fill_level_pct)
    n = len(nodes)
    for i in range(n):
        for j in range(i + 1, n):
            a = nodes[i]
            b = nodes[j]
            d = haversine_km(a.lat, a.lng, b.lat, b.lng)
            g.add_edge(a.id, b.id, weight=d)
    return g


def compute_route_dijkstra(
    start_node: str,
    bins: Iterable[BinNode],
    fill_threshold: float = 80.0,
) -> Tuple[List[str], float]:
    """
    Compute an ordered list of bin IDs representing a route that visits all
    bins whose fill_level_pct >= fill_threshold, starting from start_node.

    Strategy:
      - Filter to full bins (including the start node if present).
      - Build a fully connected graph with haversine distances.
      - From the current node, repeatedly choose the nearest NEXT full bin
        using Dijkstra (shortest path), append that path segment, and continue.
    """
    full_bins = [b for b in bins if b.fill_level_pct >= fill_threshold]
    if not full_bins:
        return [start_node], 0.0

    # Ensure start exists in the set; if not, include with 0 fill just for routing
    id_to_bin = {b.id: b for b in full_bins}
    if start_node not in id_to_bin:
        # pick any bin to copy coords from (or default 0,0 if unknown)
        example = full_bins[0]
        id_to_bin[start_node] = BinNode(id=start_node, lat=example.lat, lng=example.lng, fill_level_pct=0.0)

    g = build_graph(id_to_bin.values())

    current = start_node
    remaining = {b.id for b in full_bins if b.id != start_node}
    path: List[str] = [start_node]
    total = 0.0

    while remaining:
        best_cand = None
        best_dist = None
        best_path = None

        for cand in remaining:
            sp = nx.dijkstra_path(g, current, cand, weight="weight")
            dist = nx.dijkstra_path_length(g, current, cand, weight="weight")
            if best_dist is None or dist < best_dist:
                best_cand = cand
                best_dist = float(dist)
                best_path = sp

        assert best_cand is not None and best_path is not None and best_dist is not None
        # Append segment, skipping duplicate current node
        path.extend(best_path[1:])
        total += best_dist
        current = best_cand
        remaining.remove(best_cand)

    return path, total


def simulate_truck_positions(
    route: List[str],
    id_to_coords: dict[str, Tuple[float, float]],
    steps_per_leg: int = 10,
) -> List[Tuple[str, float, float]]:
    """
    Simple kinematic simulation along the route.

    Returns a list of (bin_or_segment_id, lat, lng) waypoints where the truck
    linearly interpolates between bin coordinates with 'steps_per_leg' points
    per edge.
    """
    if len(route) < 2:
        # Only start point
        if route:
            lat, lng = id_to_coords[route[0]]
            return [(route[0], lat, lng)]
        return []

    positions: List[Tuple[str, float, float]] = []
    for i in range(len(route) - 1):
        a_id = route[i]
        b_id = route[i + 1]
        (lat1, lng1) = id_to_coords[a_id]
        (lat2, lng2) = id_to_coords[b_id]
        for step in range(steps_per_leg):
            t = step / float(steps_per_leg)
            lat = lat1 + (lat2 - lat1) * t
            lng = lng1 + (lng2 - lng1) * t
            positions.append((f"{a_id}->{b_id}", lat, lng))
    # final position at last bin
    lat_end, lng_end = id_to_coords[route[-1]]
    positions.append((route[-1], lat_end, lng_end))
    return positions

