import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import networkx as nx


@dataclass
class CityNode:
    id: str
    name: str
    x: float
    y: float


@dataclass
class CityEdge:
    u: str
    v: str
    distance: float
    base_speed: float = 40.0
    congestion_factor: float = 1.0
    is_closed: bool = False

    @property
    def free_flow_time(self) -> float:
        return (self.distance / self.base_speed) * 60.0

    @property
    def travel_time(self) -> float:
        return self.free_flow_time * self.congestion_factor


class CityGraph:
    def __init__(self, name: str = "Ciudad"):
        self.name = name
        self.graph = nx.Graph()
        self._max_speed: float = 60.0

    def add_node(self, node_id: str, name: str, x: float, y: float) -> None:
        self.graph.add_node(node_id, name=name, x=float(x), y=float(y))

    def add_edge(
        self,
        u: str,
        v: str,
        distance: float,
        base_speed: float = 40.0,
        congestion_factor: float = 1.0,
        is_closed: bool = False,
    ) -> None:
        if base_speed > self._max_speed:
            self._max_speed = base_speed
        self.graph.add_edge(
            u,
            v,
            distance=float(distance),
            base_speed=float(base_speed),
            congestion_factor=float(congestion_factor),
            is_closed=bool(is_closed),
        )

    def get_node(self, node_id: str) -> Optional[CityNode]:
        if node_id not in self.graph.nodes:
            return None
        data = self.graph.nodes[node_id]
        return CityNode(
            id=node_id,
            name=data.get("name", node_id),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
        )

    def get_nodes(self) -> Dict[str, CityNode]:
        nodes = {}
        for nid, data in self.graph.nodes(data=True):
            nodes[nid] = CityNode(
                id=nid,
                name=data.get("name", nid),
                x=data.get("x", 0.0),
                y=data.get("y", 0.0),
            )
        return nodes

    def get_edge(self, u: str, v: str) -> Optional[CityEdge]:
        if not self.graph.has_edge(u, v):
            return None
        data = self.graph.edges[u, v]
        return CityEdge(
            u=u,
            v=v,
            distance=data["distance"],
            base_speed=data.get("base_speed", 40.0),
            congestion_factor=data.get("congestion_factor", 1.0),
            is_closed=data.get("is_closed", False),
        )

    def get_edges(self) -> List[CityEdge]:
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append(
                CityEdge(
                    u=u,
                    v=v,
                    distance=data["distance"],
                    base_speed=data.get("base_speed", 40.0),
                    congestion_factor=data.get("congestion_factor", 1.0),
                    is_closed=data.get("is_closed", False),
                )
            )
        return edges

    def get_neighbors(self, node_id: str) -> List[str]:
        if node_id not in self.graph:
            return []
        return list(self.graph.neighbors(node_id))

    def get_traversal_cost(self, u: str, v: str) -> Optional[float]:
        edge = self.get_edge(u, v)
        if edge is None or edge.is_closed:
            return None
        return edge.travel_time

    def get_distance(self, u: str, v: str) -> Optional[float]:
        edge = self.get_edge(u, v)
        if edge is None:
            return None
        return edge.distance

    def set_edge_congestion(self, u: str, v: str, factor: float) -> bool:
        if not self.graph.has_edge(u, v):
            return False
        self.graph.edges[u, v]["congestion_factor"] = max(1.0, float(factor))
        return True

    def set_edge_closed(self, u: str, v: str, closed: bool) -> bool:
        if not self.graph.has_edge(u, v):
            return False
        self.graph.edges[u, v]["is_closed"] = bool(closed)
        return True

    def reset_traffic_conditions(self) -> None:
        for _, _, data in self.graph.edges(data=True):
            data["congestion_factor"] = 1.0
            data["is_closed"] = False

    def euclidean_distance(self, node_a: str, node_b: str) -> float:
        na = self.get_node(node_a)
        nb = self.get_node(node_b)
        if na is None or nb is None:
            return 0.0
        return math.hypot(na.x - nb.x, na.y - nb.y)

    def heuristic(self, node: str, goal: str) -> float:
        dist_km = self.euclidean_distance(node, goal)
        return (dist_km / self._max_speed) * 60.0


def create_default_city() -> CityGraph:
    city = CityGraph("Metrópolis Central")

    nodes = [
        ("N1", "Plaza Mayor", 0.0, 0.0),
        ("N2", "Distrito Financiero", 2.0, 0.5),
        ("N3", "Parque Norte", 0.5, 2.5),
        ("N4", "Estación Central", -1.8, 1.0),
        ("N5", "Zona Universitaria", -2.0, -1.5),
        ("N6", "Avenida Costanera", 0.8, -2.0),
        ("N7", "Centro Histórico", -0.5, -0.8),
        ("N8", "Terminal Sur", 0.0, -3.5),
        ("N9", "Polígono Industrial", 3.5, 1.8),
        ("N10", "Hospital General", -2.8, 2.5),
        ("N11", "Centro Comercial Este", 3.0, -1.0),
        ("N12", "Mirador Poniente", -3.5, 0.0),
        ("N13", "Bulevar Los Álamos", 1.8, 2.2),
        ("N14", "Puente San Martín", -1.0, 2.0),
        ("N15", "Rotonda La Paz", 2.2, -2.5),
        ("N16", "Puerta Norte", 0.5, 4.0),
    ]

    for nid, name, x, y in nodes:
        city.add_node(nid, name, x, y)

    edges = [
        ("N1", "N2", 2.1, 50.0),
        ("N1", "N3", 2.6, 45.0),
        ("N1", "N4", 2.1, 40.0),
        ("N1", "N7", 0.9, 30.0),
        ("N2", "N9", 2.0, 55.0),
        ("N2", "N11", 1.8, 50.0),
        ("N2", "N13", 1.7, 45.0),
        ("N3", "N13", 1.3, 40.0),
        ("N3", "N14", 1.6, 40.0),
        ("N3", "N16", 1.5, 50.0),
        ("N4", "N10", 1.8, 45.0),
        ("N4", "N12", 2.0, 40.0),
        ("N4", "N14", 1.3, 35.0),
        ("N5", "N7", 1.7, 35.0),
        ("N5", "N12", 2.1, 40.0),
        ("N6", "N7", 1.8, 40.0),
        ("N6", "N8", 1.7, 50.0),
        ("N6", "N15", 1.5, 45.0),
        ("N7", "N1", 0.9, 30.0),
        ("N8", "N15", 2.4, 50.0),
        ("N9", "N13", 1.8, 50.0),
        ("N9", "N16", 3.7, 60.0),
        ("N10", "N14", 1.9, 40.0),
        ("N11", "N15", 1.7, 45.0),
        ("N13", "N16", 2.2, 55.0),
    ]

    for u, v, dist, speed in edges:
        city.add_edge(u, v, distance=dist, base_speed=speed)

    return city


def create_grid_city(rows: int, cols: int, step_km: float = 1.0) -> CityGraph:
    city = CityGraph(f"Malla {rows}x{cols}")
    for r in range(rows):
        for c in range(cols):
            nid = f"R{r}C{c}"
            city.add_node(nid, f"Intersección ({r},{c})", c * step_km, r * step_km)

    for r in range(rows):
        for c in range(cols):
            u = f"R{r}C{c}"
            if c + 1 < cols:
                v_right = f"R{r}C{c+1}"
                city.add_edge(u, v_right, distance=step_km, base_speed=40.0)
            if r + 1 < rows:
                v_down = f"R{r+1}C{c}"
                city.add_edge(u, v_down, distance=step_km, base_speed=40.0)
    return city
