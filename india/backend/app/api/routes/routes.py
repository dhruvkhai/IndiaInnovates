import networkx as nx
from fastapi import APIRouter

from app.schemas import OptimizeRouteRequest, OptimizeRouteResponse


router = APIRouter()


@router.post("/optimize", response_model=OptimizeRouteResponse)
async def optimize_route(payload: OptimizeRouteRequest):
    """
    Starter route optimization using shortest paths.
    For real deployments, you might use VRP/TSP heuristics; this is a minimal baseline.
    """
    g = nx.Graph()
    for u, v, d in payload.edges:
        g.add_edge(u, v, weight=float(d))

    start = payload.start_node
    remaining = [n for n in payload.nodes if n != start]

    path = [start]
    total = 0.0
    current = start

    # Greedy "nearest next" using shortest-path distance on the graph
    while remaining:
        best = None
        best_dist = None
        best_sp = None
        for cand in remaining:
            sp = nx.shortest_path(g, current, cand, weight="weight")
            dist = nx.shortest_path_length(g, current, cand, weight="weight")
            if best_dist is None or dist < best_dist:
                best = cand
                best_dist = float(dist)
                best_sp = sp

        # Append shortest path (skip current duplicate)
        assert best is not None and best_sp is not None and best_dist is not None
        path.extend(best_sp[1:])
        total += best_dist
        current = best
        remaining.remove(best)

    return OptimizeRouteResponse(path=path, total_distance_km=round(total, 3))

