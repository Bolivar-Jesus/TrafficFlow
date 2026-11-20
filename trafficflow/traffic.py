from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from trafficflow.graph import CityGraph


class TrafficEventType(Enum):
    CONGESTION_APPLIED = "CONGESTION_APPLIED"
    ROAD_CLOSED = "ROAD_CLOSED"
    ROAD_REOPENED = "ROAD_REOPENED"
    CONDITIONS_RESET = "CONDITIONS_RESET"


@dataclass
class TrafficEvent:
    event_type: TrafficEventType
    u: Optional[str] = None
    v: Optional[str] = None
    value: Optional[float] = None
    description: str = ""


class TrafficObserver(ABC):
    @abstractmethod
    def on_traffic_changed(self, event: TrafficEvent) -> None:
        pass


class TrafficSubject(ABC):
    def __init__(self) -> None:
        self._observers: List[TrafficObserver] = []

    def attach(self, observer: TrafficObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: TrafficObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: TrafficEvent) -> None:
        for observer in list(self._observers):
            observer.on_traffic_changed(event)


class TrafficManager(TrafficSubject):
    def __init__(self, graph: CityGraph):
        super().__init__()
        self.graph = graph

    def apply_congestion(self, u: str, v: str, factor: float) -> bool:
        factor = max(1.0, float(factor))
        success = self.graph.set_edge_congestion(u, v, factor)
        if success:
            event = TrafficEvent(
                event_type=TrafficEventType.CONGESTION_APPLIED,
                u=u,
                v=v,
                value=factor,
                description=f"Congestión factor {factor:.1f}x aplicada en tramo {u} - {v}.",
            )
            self.notify(event)
        return success

    def close_road(self, u: str, v: str) -> bool:
        success = self.graph.set_edge_closed(u, v, True)
        if success:
            event = TrafficEvent(
                event_type=TrafficEventType.ROAD_CLOSED,
                u=u,
                v=v,
                value=None,
                description=f"Vía cerrada temporalmente entre {u} y {v}.",
            )
            self.notify(event)
        return success

    def reopen_road(self, u: str, v: str) -> bool:
        success = self.graph.set_edge_closed(u, v, False)
        if success:
            event = TrafficEvent(
                event_type=TrafficEventType.ROAD_REOPENED,
                u=u,
                v=v,
                value=None,
                description=f"Vía reabierta entre {u} y {v}.",
            )
            self.notify(event)
        return success

    def reset_all(self) -> None:
        self.graph.reset_traffic_conditions()
        event = TrafficEvent(
            event_type=TrafficEventType.CONDITIONS_RESET,
            description="Condiciones de tráfico y cierres restablecidos a valores iniciales.",
        )
        self.notify(event)

    def get_active_congestions(self) -> List[Tuple[str, str, float]]:
        congestions = []
        for edge in self.graph.get_edges():
            if edge.congestion_factor > 1.0 and not edge.is_closed:
                congestions.append((edge.u, edge.v, edge.congestion_factor))
        return congestions

    def get_closed_roads(self) -> List[Tuple[str, str]]:
        closed = []
        for edge in self.graph.get_edges():
            if edge.is_closed:
                closed.append((edge.u, edge.v))
        return closed


class RouteStateObserver(TrafficObserver):
    """Observador que registra cambios y mantiene bandera de invalidación de rutas previas."""

    def __init__(self) -> None:
        self.last_event: Optional[TrafficEvent] = None
        self.is_route_invalidated: bool = False
        self.history: List[TrafficEvent] = []

    def on_traffic_changed(self, event: TrafficEvent) -> None:
        self.last_event = event
        self.is_route_invalidated = True
        self.history.append(event)

    def clear_invalidation(self) -> None:
        self.is_route_invalidated = False
