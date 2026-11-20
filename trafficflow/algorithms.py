import heapq
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from trafficflow.graph import CityGraph


@dataclass
class RouteResult:
    algorithm: str
    success: bool
    path: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    nodes_explored: int = 0
    execution_time_ms: float = 0.0
    message: str = ""


class RouteStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def find_route(
        self, graph: CityGraph, origin: str, destination: str
    ) -> RouteResult:
        pass

    def _compute_path_metrics(
        self, graph: CityGraph, path: List[str]
    ) -> tuple[float, float]:
        dist = 0.0
        ttime = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge = graph.get_edge(u, v)
            if edge:
                dist += edge.distance
                ttime += edge.travel_time
        return round(dist, 3), round(ttime, 3)


class DijkstraStrategy(RouteStrategy):
    @property
    def name(self) -> str:
        return "Dijkstra"

    def find_route(
        self, graph: CityGraph, origin: str, destination: str
    ) -> RouteResult:
        start_time = time.perf_counter()

        if origin not in graph.graph or destination not in graph.graph:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RouteResult(
                algorithm=self.name,
                success=False,
                execution_time_ms=round(elapsed_ms, 3),
                message="El origen o destino no existe en el mapa.",
            )

        if origin == destination:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RouteResult(
                algorithm=self.name,
                success=True,
                path=[origin],
                total_distance=0.0,
                total_time=0.0,
                nodes_explored=1,
                execution_time_ms=round(elapsed_ms, 3),
                message="Origen y destino son el mismo punto.",
            )

        # Min-heap: (cost_g, tie_breaker, node)
        counter = 0
        pq = [(0.0, counter, origin)]
        min_cost = {origin: 0.0}
        parent = {}
        visited = set()
        nodes_explored = 0

        while pq:
            cost, _, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)
            nodes_explored += 1

            if current == destination:
                break

            for neighbor in graph.get_neighbors(current):
                edge = graph.get_edge(current, neighbor)
                if edge is None or edge.is_closed:
                    continue

                new_cost = cost + edge.travel_time
                if new_cost < min_cost.get(neighbor, float("inf")):
                    min_cost[neighbor] = new_cost
                    parent[neighbor] = current
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, neighbor))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if destination not in parent and origin != destination:
            return RouteResult(
                algorithm=self.name,
                success=False,
                path=[],
                total_distance=0.0,
                total_time=0.0,
                nodes_explored=nodes_explored,
                execution_time_ms=round(elapsed_ms, 3),
                message="No se encontró una ruta disponible entre los puntos seleccionados.",
            )

        # Reconstruct path
        path = []
        curr: Optional[str] = destination
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

        dist, total_time = self._compute_path_metrics(graph, path)

        return RouteResult(
            algorithm=self.name,
            success=True,
            path=path,
            total_distance=dist,
            total_time=total_time,
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed_ms, 3),
            message="Ruta calculada exitosamente.",
        )


class AStarStrategy(RouteStrategy):
    @property
    def name(self) -> str:
        return "A*"

    def find_route(
        self, graph: CityGraph, origin: str, destination: str
    ) -> RouteResult:
        start_time = time.perf_counter()

        if origin not in graph.graph or destination not in graph.graph:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RouteResult(
                algorithm=self.name,
                success=False,
                execution_time_ms=round(elapsed_ms, 3),
                message="El origen o destino no existe en el mapa.",
            )

        if origin == destination:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RouteResult(
                algorithm=self.name,
                success=True,
                path=[origin],
                total_distance=0.0,
                total_time=0.0,
                nodes_explored=1,
                execution_time_ms=round(elapsed_ms, 3),
                message="Origen y destino son el mismo punto.",
            )

        # Min-heap: (f_score, tie_breaker, current_node, g_score)
        counter = 0
        h_start = graph.heuristic(origin, destination)
        pq = [(h_start, counter, origin, 0.0)]
        g_scores = {origin: 0.0}
        parent = {}
        visited = set()
        nodes_explored = 0

        while pq:
            f, _, current, g = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)
            nodes_explored += 1

            if current == destination:
                break

            for neighbor in graph.get_neighbors(current):
                edge = graph.get_edge(current, neighbor)
                if edge is None or edge.is_closed:
                    continue

                tentative_g = g + edge.travel_time
                if tentative_g < g_scores.get(neighbor, float("inf")):
                    g_scores[neighbor] = tentative_g
                    parent[neighbor] = current
                    counter += 1
                    h_val = graph.heuristic(neighbor, destination)
                    f_val = tentative_g + h_val
                    heapq.heappush(pq, (f_val, counter, neighbor, tentative_g))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if destination not in parent and origin != destination:
            return RouteResult(
                algorithm=self.name,
                success=False,
                path=[],
                total_distance=0.0,
                total_time=0.0,
                nodes_explored=nodes_explored,
                execution_time_ms=round(elapsed_ms, 3),
                message="No se encontró una ruta disponible entre los puntos seleccionados.",
            )

        # Reconstruct path
        path = []
        curr: Optional[str] = destination
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

        dist, total_time = self._compute_path_metrics(graph, path)

        return RouteResult(
            algorithm=self.name,
            success=True,
            path=path,
            total_distance=dist,
            total_time=total_time,
            nodes_explored=nodes_explored,
            execution_time_ms=round(elapsed_ms, 3),
            message="Ruta calculada exitosamente.",
        )


class RoutePlanner:
    def __init__(self, strategy: Optional[RouteStrategy] = None):
        self._strategy: RouteStrategy = strategy or DijkstraStrategy()

    @property
    def strategy(self) -> RouteStrategy:
        return self._strategy

    def set_strategy(self, strategy: RouteStrategy) -> None:
        self._strategy = strategy

    def calculate_route(
        self, graph: CityGraph, origin: str, destination: str
    ) -> RouteResult:
        return self._strategy.find_route(graph, origin, destination)
