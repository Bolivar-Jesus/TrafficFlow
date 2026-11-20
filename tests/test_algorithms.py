import pytest
from trafficflow.graph import CityGraph, create_default_city
from trafficflow.algorithms import (
    DijkstraStrategy,
    AStarStrategy,
    RoutePlanner,
    RouteResult,
)


@pytest.fixture
def small_graph() -> CityGraph:
    """Grafo de 4 nodos con distancias y tiempos conocidos:
       A --(1km, 60km/h: 1min)--> B --(1km, 60km/h: 1min)--> D (total: 2min, 2km)
       A --(3km, 30km/h: 6min)--> C --(1km, 60km/h: 1min)--> D (total: 7min, 4km)
    """
    g = CityGraph("GrafoPrueba")
    g.add_node("A", "Nodo A", 0.0, 0.0)
    g.add_node("B", "Nodo B", 1.0, 0.0)
    g.add_node("C", "Nodo C", 0.0, 3.0)
    g.add_node("D", "Nodo D", 1.0, 3.0)

    g.add_edge("A", "B", distance=1.0, base_speed=60.0)
    g.add_edge("B", "D", distance=1.0, base_speed=60.0)
    g.add_edge("A", "C", distance=3.0, base_speed=30.0)
    g.add_edge("C", "D", distance=1.0, base_speed=60.0)
    return g


@pytest.fixture
def default_city() -> CityGraph:
    return create_default_city()


def test_dijkstra_small_graph(small_graph: CityGraph):
    strategy = DijkstraStrategy()
    result = strategy.find_route(small_graph, "A", "D")

    assert result.success is True
    assert result.path == ["A", "B", "D"]
    assert result.total_distance == pytest.approx(2.0, rel=1e-3)
    assert result.total_time == pytest.approx(2.0, rel=1e-3)
    assert result.nodes_explored >= 2
    assert result.execution_time_ms >= 0.0


def test_astar_small_graph(small_graph: CityGraph):
    strategy = AStarStrategy()
    result = strategy.find_route(small_graph, "A", "D")

    assert result.success is True
    assert result.path == ["A", "B", "D"]
    assert result.total_distance == pytest.approx(2.0, rel=1e-3)
    assert result.total_time == pytest.approx(2.0, rel=1e-3)
    assert result.nodes_explored >= 1
    assert result.execution_time_ms >= 0.0


def test_dijkstra_astar_optimal_cost_coincidence(default_city: CityGraph):
    dijkstra = DijkstraStrategy()
    astar = AStarStrategy()

    pairs = [
        ("N1", "N16"),
        ("N5", "N9"),
        ("N8", "N10"),
        ("N12", "N15"),
        ("N7", "N13"),
    ]

    for orig, dest in pairs:
        res_d = dijkstra.find_route(default_city, orig, dest)
        res_a = astar.find_route(default_city, orig, dest)

        assert res_d.success is True
        assert res_a.success is True
        # Costo de viaje óptimo debe ser idéntico
        assert res_d.total_time == pytest.approx(res_a.total_time, abs=1e-3), (
            f"Fallo en par {orig} -> {dest}: Dijkstra={res_d.total_time}, A*={res_a.total_time}"
        )
        # Distancia física asociada también coincide para la misma ruta óptima
        assert res_d.total_distance == pytest.approx(res_a.total_distance, abs=1e-3)


def test_same_origin_and_destination(default_city: CityGraph):
    dijkstra = DijkstraStrategy()
    astar = AStarStrategy()

    res_d = dijkstra.find_route(default_city, "N1", "N1")
    assert res_d.success is True
    assert res_d.path == ["N1"]
    assert res_d.total_distance == 0.0
    assert res_d.total_time == 0.0
    assert res_d.nodes_explored == 1

    res_a = astar.find_route(default_city, "N1", "N1")
    assert res_a.success is True
    assert res_a.path == ["N1"]
    assert res_a.total_distance == 0.0
    assert res_a.total_time == 0.0
    assert res_a.nodes_explored == 1


def test_disconnected_points():
    g = CityGraph("GrafoDesconectado")
    g.add_node("A", "A", 0, 0)
    g.add_node("B", "B", 1, 0)
    g.add_node("X", "X", 10, 10)
    g.add_edge("A", "B", 1.0, 40.0)

    dijkstra = DijkstraStrategy()
    astar = AStarStrategy()

    res_d = dijkstra.find_route(g, "A", "X")
    assert res_d.success is False
    assert res_d.path == []
    assert "No se encontró" in res_d.message

    res_a = astar.find_route(g, "A", "X")
    assert res_a.success is False
    assert res_a.path == []
    assert "No se encontró" in res_a.message


def test_nonexistent_nodes(default_city: CityGraph):
    dijkstra = DijkstraStrategy()
    res = dijkstra.find_route(default_city, "INEXISTENTE", "N1")
    assert res.success is False
    assert "no existe" in res.message


def test_strategy_pattern_behavior(default_city: CityGraph):
    planner = RoutePlanner(DijkstraStrategy())
    assert planner.strategy.name == "Dijkstra"
    res1 = planner.calculate_route(default_city, "N1", "N9")
    assert res1.algorithm == "Dijkstra"
    assert res1.success is True

    # Intercambiar estrategia en tiempo de ejecución
    planner.set_strategy(AStarStrategy())
    assert planner.strategy.name == "A*"
    res2 = planner.calculate_route(default_city, "N1", "N9")
    assert res2.algorithm == "A*"
    assert res2.success is True
    assert res1.total_time == pytest.approx(res2.total_time, abs=1e-3)
