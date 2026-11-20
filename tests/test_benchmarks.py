import pytest
from trafficflow.graph import create_default_city, create_grid_city
from trafficflow.metrics import run_benchmark


@pytest.mark.parametrize(
    "name,graph,origin,destination",
    [
        ("Ciudad Estándar (16 nodos, 24 vías)", create_default_city(), "N1", "N16"),
        ("Malla Pequeña 3x3 (9 nodos, 12 vías)", create_grid_city(3, 3), "R0C0", "R2C2"),
        ("Malla Mediana 7x7 (49 nodos, 84 vías)", create_grid_city(7, 7), "R0C0", "R6C6"),
        ("Malla Grande 12x12 (144 nodos, 264 vías)", create_grid_city(12, 12), "R0C0", "R11C11"),
    ],
)
def test_performance_comparison_different_sizes(name, graph, origin, destination):
    iterations = 10
    bench = run_benchmark(graph, origin, destination, iterations=iterations)

    d_res = bench["Dijkstra"]
    a_res = bench["A*"]

    # Ambos deben encontrar la ruta óptima
    assert d_res["success"] is True
    assert a_res["success"] is True

    # El costo óptimo debe ser idéntico
    assert d_res["travel_time_min"] == pytest.approx(a_res["travel_time_min"], abs=1e-3)
    assert d_res["distance_km"] == pytest.approx(a_res["distance_km"], abs=1e-3)

    # Validar que los nodos explorados y tiempos sean coherentes
    assert d_res["nodes_explored"] >= 1
    assert a_res["nodes_explored"] >= 1
    assert d_res["avg_execution_time_ms"] >= 0.0
    assert a_res["avg_execution_time_ms"] >= 0.0
