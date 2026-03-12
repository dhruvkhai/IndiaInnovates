from fastapi import APIRouter

from app.schemas import OptimizeRouteRequest, OptimizeRouteResponse
from app.services.route_optimization import BinNode, build_graph, compute_route_dijkstra


router = APIRouter()


@router.post("/optimize", response_model=OptimizeRouteResponse)
async def optimize_route(payload: OptimizeRouteRequest):
    """
    Route optimization entrypoint.

    Expects a list of nodes and edges; uses Dijkstra-based nearest-next
    routing on the provided graph. This is a generic wrapper over the
    reusable service in app.services.route_optimization.
    """
    # Map incoming nodes (string IDs) to BinNode with dummy fill levels (100% -> always selected)
    # If you want to incorporate real fill levels, construct BinNode objects using those values.
    bins = [BinNode(id=n, lat=0.0, lng=0.0, fill_level_pct=100.0) for n in payload.nodes]

    # Build graph using provided edges (distance already given)
    # Here we short-circuit the internal graph building by simply relying on the
    # service's Dijkstra routing to order nodes, ignoring haversine.
    # For simplicity, we reuse compute_route_dijkstra's algorithm but we won't
    # use its own build_graph; distances are already in payload.
    # To avoid duplicating logic, we reconstruct a small "full bins" set:

    # NOTE: For this generic endpoint we don't know true coordinates; we set them all to 0,0.
    # The actual optimization quality for distances is determined by the caller via payload.edges.
    # We therefore fall back to a simple Dijkstra nearest-next by reusing the service with a neutral threshold.

    # Since compute_route_dijkstra currently builds a complete graph from coordinates,
    # and this endpoint already receives a graph, we keep the existing behavior here:
    # shortest path over payload.edges using Dijkstra.

    from math import inf
    import networkx as nx

    g = nx.Graph()
    for u, v, d in payload.edges:
        g.add_edge(u, v, weight=float(d))

    start = payload.start_node
    remaining = [n for n in payload.nodes if n != start]

    path = [start]
    total = 0.0
    current = start

    while remaining:
        best_cand = None
        best_dist = inf
        best_path = None
        for cand in remaining:
            sp = nx.dijkstra_path(g, current, cand, weight="weight")
            dist = nx.dijkstra_path_length(g, current, cand, weight="weight")
            if dist < best_dist:
                best_dist = dist
                best_cand = cand
                best_path = sp

        assert best_cand is not None and best_path is not None
        path.extend(best_path[1:])
        total += best_dist
        current = best_cand
        remaining.remove(best_cand)

    return OptimizeRouteResponse(path=path, total_distance_km=round(float(total), 3))

