import pytest
from trafficflow.graph import create_default_city
from trafficflow.algorithms import DijkstraStrategy, AStarStrategy
from trafficflow.metrics import compare_strategies, run_benchmark


@pytest.fixture
def default_city():
    return create_default_city()


def test_accurate_distance_and_time_calculation(default_city):
    # Probar tramo directo conocido: N1 - N7
    # Distancia: 0.9 km, Velocidad: 30 km/h -> Tiempo libre = (0.9 / 30) * 60 = 1.8 min
    dijkstra = DijkstraStrategy()
    result = dijkstra.find_route(default_city, "N1", "N7")

    assert result.success is True
    assert result.path == ["N1", "N7"]
    assert result.total_distance == pytest.approx(0.9, rel=1e-3)
    assert result.total_time == pytest.approx(1.8, rel=1e-3)


def test_compare_strategies_output_validity(default_city):
    comparison = compare_strategies(default_city, "N1", "N16")

    assert "Dijkstra" in comparison
    assert "A*" in comparison

    d_res = comparison["Dijkstra"]
    a_res = comparison["A*"]

    assert d_res.success is True
    assert a_res.success is True

    # Comprobación de tipos y rangos válidos
    assert d_res.distance_km > 0
    assert a_res.distance_km > 0
    assert d_res.travel_time_min > 0
    assert a_res.travel_time_min > 0
    assert d_res.execution_time_ms >= 0.0
    assert a_res.execution_time_ms >= 0.0
    assert d_res.nodes_explored >= 1
    assert a_res.nodes_explored >= 1

    # Coincidencia de tiempo de viaje óptimo
    assert d_res.travel_time_min == pytest.approx(a_res.travel_time_min, abs=1e-3)
    assert d_res.distance_km == pytest.approx(a_res.distance_km, abs=1e-3)

    # Distinción estricta: tiempo de viaje (minutos) != tiempo de ejecución (milisegundos)
    assert d_res.travel_time_min != d_res.execution_time_ms
    assert a_res.travel_time_min != a_res.execution_time_ms


def test_run_benchmark_averages(default_city):
    benchmark = run_benchmark(default_city, "N1", "N16", iterations=5)

    assert "Dijkstra" in benchmark
    assert "A*" in benchmark

    for algo in ["Dijkstra", "A*"]:
        entry = benchmark[algo]
        assert entry["iterations"] == 5
        assert entry["avg_execution_time_ms"] >= 0.0
        assert entry["min_execution_time_ms"] >= 0.0
        assert entry["avg_execution_time_ms"] >= entry["min_execution_time_ms"]
        assert entry["nodes_explored"] > 0
