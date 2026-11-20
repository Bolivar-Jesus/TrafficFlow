import pytest
from trafficflow.graph import CityGraph, create_default_city
from trafficflow.algorithms import DijkstraStrategy, AStarStrategy
from trafficflow.traffic import (
    TrafficManager,
    TrafficObserver,
    TrafficEvent,
    TrafficEventType,
    RouteStateObserver,
)


@pytest.fixture
def city_and_manager():
    graph = create_default_city()
    manager = TrafficManager(graph)
    return graph, manager


def test_congestion_increases_travel_time_not_distance(city_and_manager):
    graph, manager = city_and_manager
    dijkstra = DijkstraStrategy()

    # Ruta inicial N1 -> N2
    res_base = dijkstra.find_route(graph, "N1", "N2")
    base_dist = res_base.total_distance
    base_time = res_base.total_time

    # Aplicar congestión severa (factor 3.5x) en tramo N1 - N2
    success = manager.apply_congestion("N1", "N2", 3.5)
    assert success is True

    edge = graph.get_edge("N1", "N2")
    assert edge.congestion_factor == 3.5
    assert edge.distance == pytest.approx(2.1)

    # Recalcular ruta: la distancia física del tramo sigue igual, el tiempo aumenta o toma desvío
    res_congested = dijkstra.find_route(graph, "N1", "N2")
    assert res_congested.success is True
    assert res_congested.total_time >= base_time


def test_road_closure_excludes_edge(city_and_manager):
    graph, manager = city_and_manager
    dijkstra = DijkstraStrategy()

    # En grafo inicial, N1 -> N2 directo es ["N1", "N2"]
    res_init = dijkstra.find_route(graph, "N1", "N2")
    assert res_init.path == ["N1", "N2"]

    # Cerrar tramo N1 - N2
    manager.close_road("N1", "N2")
    assert graph.get_edge("N1", "N2").is_closed is True

    # Recalcular: la ruta no debe contener el tramo cerrado N1 - N2
    res_rerouted = dijkstra.find_route(graph, "N1", "N2")
    assert res_rerouted.success is True
    assert res_rerouted.path != ["N1", "N2"]
    for i in range(len(res_rerouted.path) - 1):
        segment = {res_rerouted.path[i], res_rerouted.path[i + 1]}
        assert segment != {"N1", "N2"}


def test_reset_traffic_conditions(city_and_manager):
    graph, manager = city_and_manager
    dijkstra = DijkstraStrategy()

    # Guardar métricas iniciales N1 -> N16
    initial_res = dijkstra.find_route(graph, "N1", "N16")

    # Modificar vías con congestión y cierres
    manager.apply_congestion("N1", "N3", 4.0)
    manager.close_road("N3", "N16")

    modified_res = dijkstra.find_route(graph, "N1", "N16")
    assert modified_res.total_time != initial_res.total_time

    # Restablecer
    manager.reset_all()

    reset_res = dijkstra.find_route(graph, "N1", "N16")
    assert reset_res.path == initial_res.path
    assert reset_res.total_time == pytest.approx(initial_res.total_time, abs=1e-3)
    assert reset_res.total_distance == pytest.approx(initial_res.total_distance, abs=1e-3)
    assert len(manager.get_active_congestions()) == 0
    assert len(manager.get_closed_roads()) == 0


def test_observer_pattern_notifications(city_and_manager):
    graph, manager = city_and_manager
    observer = RouteStateObserver()
    manager.attach(observer)

    assert observer.last_event is None
    assert observer.is_route_invalidated is False

    # Evento de congestión
    manager.apply_congestion("N1", "N2", 2.0)
    assert observer.is_route_invalidated is True
    assert observer.last_event is not None
    assert observer.last_event.event_type == TrafficEventType.CONGESTION_APPLIED
    assert observer.last_event.value == 2.0

    # Limpiar estado del observador
    observer.clear_invalidation()
    assert observer.is_route_invalidated is False

    # Evento de cierre
    manager.close_road("N2", "N9")
    assert observer.is_route_invalidated is True
    assert observer.last_event.event_type == TrafficEventType.ROAD_CLOSED

    # Evento de reapertura
    manager.reopen_road("N2", "N9")
    assert observer.last_event.event_type == TrafficEventType.ROAD_REOPENED

    # Evento de reset
    manager.reset_all()
    assert observer.last_event.event_type == TrafficEventType.CONDITIONS_RESET
    assert len(observer.history) == 4

    # Desuscripción
    manager.detach(observer)
    manager.apply_congestion("N1", "N4", 3.0)
    assert len(observer.history) == 4  # No se agregaron más eventos
