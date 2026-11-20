import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from trafficflow.graph import CityGraph
from trafficflow.algorithms import (
    RouteStrategy,
    DijkstraStrategy,
    AStarStrategy,
    RouteResult,
)


@dataclass
class ComparisonItem:
    algorithm: str
    success: bool
    path: List[str]
    path_str: str
    distance_km: float
    travel_time_min: float
    execution_time_ms: float
    nodes_explored: int
    message: str


def compare_strategies(
    graph: CityGraph,
    origin: str,
    destination: str,
    strategies: Optional[List[RouteStrategy]] = None,
) -> Dict[str, ComparisonItem]:
    if strategies is None:
        strategies = [DijkstraStrategy(), AStarStrategy()]

    results: Dict[str, ComparisonItem] = {}

    for strat in strategies:
        res: RouteResult = strat.find_route(graph, origin, destination)
        results[strat.name] = ComparisonItem(
            algorithm=strat.name,
            success=res.success,
            path=res.path,
            path_str=" -> ".join(res.path) if res.path else "Sin ruta",
            distance_km=res.total_distance,
            travel_time_min=res.total_time,
            execution_time_ms=res.execution_time_ms,
            nodes_explored=res.nodes_explored,
            message=res.message,
        )

    return results


def run_benchmark(
    graph: CityGraph,
    origin: str,
    destination: str,
    iterations: int = 10,
) -> Dict[str, dict]:
    strategies = [DijkstraStrategy(), AStarStrategy()]
    summary = {}

    for strat in strategies:
        times = []
        last_res: Optional[RouteResult] = None

        for _ in range(iterations):
            t0 = time.perf_counter()
            res = strat.find_route(graph, origin, destination)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            times.append(elapsed_ms)
            last_res = res

        avg_time = sum(times) / len(times)
        min_time = min(times)

        summary[strat.name] = {
            "algorithm": strat.name,
            "success": last_res.success if last_res else False,
            "path": last_res.path if last_res else [],
            "distance_km": last_res.total_distance if last_res else 0.0,
            "travel_time_min": last_res.total_time if last_res else 0.0,
            "nodes_explored": last_res.nodes_explored if last_res else 0,
            "avg_execution_time_ms": round(avg_time, 4),
            "min_execution_time_ms": round(min_time, 4),
            "iterations": iterations,
        }

    return summary
