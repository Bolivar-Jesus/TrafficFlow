# Informe de Resultados de Pruebas Automatizadas y Rendimiento
**Proyecto:** TrafficFlow — Simulador de Rutas Urbanas  
**Actividad:** Arquitectura de Software — Evaluación y Optimización de Arquitecturas  

---

## 1. Información General del Entorno de Ejecución

- **Fecha de ejecución:** 20 de noviembre de 2026
- **Sistema Operativo:** Microsoft Windows 11 Home (x64)
- **Intérprete de Lenguaje:** Python 3.12.4
- **Herramienta de Pruebas:** Pytest 9.2.0 (motor Pluggy 1.7.0)
- **Bibliotecas Principales:**
  - NetworkX 3.7
  - Streamlit 1.67.0
  - Matplotlib 3.11.2
  - PlantUML 0.3.0

---

## 2. Comandos Ejecutados

Para la verificación funcional de la suite completa:
```powershell
pytest -v
```

Para la ejecución y recolección de mediciones de rendimiento empírico:
```powershell
python -m pytest tests/test_benchmarks.py -v
```

---

## 3. Resumen Cuantitativo de Pruebas

| Métrica | Valor |
| :--- | :--- |
| **Total de pruebas automatizadas ejecutadas** | **18** |
| **Pruebas aprobadas (Passed)** | **18** (100%) |
| **Pruebas fallidas (Failed)** | **0** (0%) |
| **Pruebas omitidas (Skipped)** | **0** |
| **Tiempo total de ejecución de la suite** | **1.87 segundos** |

---

## 4. Detalle de Pruebas Unitarias y Funcionales

| Módulo de Prueba | Identificador de Prueba | Objetivo de Verificación | Resultado |
| :--- | :--- | :--- | :--- |
| `test_algorithms.py` | `test_dijkstra_small_graph` | Verificación de ruta mínima, distancia y tiempo en grafo conocido con Dijkstra. | **Aprobado** |
| `test_algorithms.py` | `test_astar_small_graph` | Verificación de ruta mínima, distancia y tiempo en grafo conocido con A*. | **Aprobado** |
| `test_algorithms.py` | `test_dijkstra_astar_optimal_cost_coincidence` | Demostración de igualdad estricta de costo óptimo entre Dijkstra y A* en 5 pares origen-destino. | **Aprobado** |
| `test_algorithms.py` | `test_same_origin_and_destination` | Comportamiento cuando origen y destino coinciden (distancia = 0, tiempo = 0). | **Aprobado** |
| `test_algorithms.py` | `test_disconnected_points` | Manejo seguro de nodos sin conectividad vial disponible (sin excepciones). | **Aprobado** |
| `test_algorithms.py` | `test_nonexistent_nodes` | Validación de identificación de nodos no registrados en el grafo. | **Aprobado** |
| `test_algorithms.py` | `test_strategy_pattern_behavior` | Verificación del desacoplamiento e intercambio dinámico de algoritmos mediante el patrón **Strategy**. | **Aprobado** |
| `test_traffic.py` | `test_congestion_increases_travel_time_not_distance` | Comprobación de que la congestión eleva el tiempo estimado sin modificar la distancia física. | **Aprobado** |
| `test_traffic.py` | `test_road_closure_excludes_edge` | Exclusión total de aristas cerradas y recálculo de desvíos válidos. | **Aprobado** |
| `test_traffic.py` | `test_reset_traffic_conditions` | Reversión exitosa de todas las congestiones y reapertura de vías al estado base. | **Aprobado** |
| `test_traffic.py` | `test_observer_pattern_notifications` | Notificación y actualización reactiva de observadores ante eventos viales mediante el patrón **Observer**. | **Aprobado** |
| `test_metrics.py` | `test_accurate_distance_and_time_calculation` | Validación matemática de fórmulas de velocidad, distancia y tiempo de viaje. | **Aprobado** |
| `test_metrics.py` | `test_compare_strategies_output_validity` | Verificación estructural de la matriz de comparación y diferenciación entre tiempo de viaje y tiempo de cómputo. | **Aprobado** |
| `test_metrics.py` | `test_run_benchmark_averages` | Consistencia estadística y cálculo de promedios en ejecuciones repetidas. | **Aprobado** |
| `test_benchmarks.py` | `test_performance_comparison_different_sizes[Ciudad Estándar]` | Evaluación comparativa en la red urbana base (16 nodos, 24 vías). | **Aprobado** |
| `test_benchmarks.py` | `test_performance_comparison_different_sizes[Malla Pequeña 3x3]` | Evaluación comparativa en cuadrícula de 9 nodos y 12 vías. | **Aprobado** |
| `test_benchmarks.py` | `test_performance_comparison_different_sizes[Malla Mediana 7x7]` | Evaluación comparativa en cuadrícula de 49 nodos y 84 vías. | **Aprobado** |
| `test_benchmarks.py` | `test_performance_comparison_different_sizes[Malla Grande 12x12]` | Evaluación comparativa en cuadrícula de 144 nodos y 264 vías. | **Aprobado** |

---

## 5. Errores Identificados y Correcciones Realizadas

Durante el proceso de desarrollo y pruebas se detectaron y solventaron los siguientes aspectos técnicos:

1. **Ajuste de secuencias de escape en cadenas de Markdown:**  
   *Problema:* En la versión 3.12 de Python, el uso de secuencias como `\*` dentro de cadenas regulares emite una advertencia de sintaxis (`SyntaxWarning: invalid escape sequence`).  
   *Corrección:* Se actualizaron las cadenas de texto a secuencias con escape explícito doble `\\*` o cadenas sin formato para garantizar compatibilidad estricta con Python 3.12 y versiones superiores.

2. **Diferenciación estricta entre métricas operativas y de rendimiento:**  
   *Problema:* Riesgo de confusión entre el tiempo de viaje estimado (magnitud del problema expresada en minutos) y el tiempo de ejecución del algoritmo (magnitud de la solución expresada en milisegundos).  
   *Corrección:* Se estructuró formalmente la clase `RouteResult` y la función `compare_strategies`, separando explícitamente `total_time` (min) de `execution_time_ms` (ms), validándolo en las pruebas unitarias.

---

## 6. Resultados Reales de Rendimiento y Benchmarking

Las pruebas de rendimiento se llevaron a cabo ejecutando **50 iteraciones controladas por cada escenario**, empleando un temporizador monotónico de alta resolución (`time.perf_counter`).

### Tabla de Mediciones Empíricas

| Escenario | Nodos | Vías | Algoritmo | Costo Óptimo (min) | Distancia (km) | Nodos Explorados | Tiempo Promedio (ms) | Tiempo Mínimo (ms) |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Ciudad Estándar** | 16 | 24 | **Dijkstra** | 5.267 | 4.100 | 11 | 0.1507 ms | 0.1453 ms |
| *(N1 ➔ N16)* | 16 | 24 | **A\*** | 5.267 | 4.100 | **3** | **0.0918 ms** | **0.0783 ms** |
| **Malla Pequeña 3x3** | 9 | 12 | **Dijkstra** | 6.000 | 4.000 | 9 | **0.1190 ms** | **0.1042 ms** |
| *(R0C0 ➔ R2C2)* | 9 | 12 | **A\*** | 6.000 | 4.000 | 9 | 0.1522 ms | 0.1484 ms |
| **Malla Mediana 7x7** | 49 | 84 | **Dijkstra** | 18.000 | 12.000 | 49 | **0.7026 ms** | **0.6502 ms** |
| *(R0C0 ➔ R6C6)* | 49 | 84 | **A\*** | 18.000 | 12.000 | 49 | 0.9245 ms | 0.8904 ms |
| **Malla Grande 12x12**| 144 | 264 | **Dijkstra** | 33.000 | 22.000 | 144 | **2.1348 ms** | **2.0061 ms** |
| *(R0C0 ➔ R11C11)* | 144 | 264 | **A\*** | 33.000 | 22.000 | 144 | 2.8515 ms | 2.6953 ms |

---

## 7. Análisis Comparativo: Dijkstra frente a A*

A partir de las mediciones reales obtenidas, se concluyen los siguientes hallazgos:

1. **Redes Urbanas Irregulares (Topología Realista):**  
   En la red de la **Ciudad Estándar**, donde las coordenadas geográficas proporcionan una guía direccional efectiva hacia el destino, **A\* demostró una superioridad notable en eficiencia de exploración**:
   - A* exploró únicamente **3 nodos** para encontrar la solución óptima, mientras que Dijkstra exploró **11 nodos** (una reducción del 72.7% en el espacio de búsqueda).
   - Como consecuencia directa, el tiempo de ejecución promedio de A* fue de **0.0918 ms**, frente a **0.1507 ms** de Dijkstra (aproximadamente un 39% más rápido).

2. **Redes Regulares en Malla Simétrica (Cuadrículas Uniformes):**  
   En las mallas ortogonales uniformes (3x3, 7x7, 12x12) donde todas las aristas poseen idéntico peso y no hay diagonales físicas:
   - Ambos algoritmos exploraron la totalidad de los nodos del espacio relevante, ya que existen múltiples caminos simétricos con el mismo costo acumulado.
   - En este escenario particular, **Dijkstra resultó ligeramente más rápido en tiempo de CPU** (2.13 ms vs. 2.85 ms en la malla 12x12). Esto se debe a que A* incurre en la sobrecarga computacional de calcular la función heurística euclidiana y gestionar las prioridades compuestas `f(n) = g(n) + h(n)` para cada arista evaluada, sin obtener una poda direccional suficiente para compensar dicho costo.

3. **Garantía de Optimalidad:**  
   En el 100% de los casos evaluados, **ambos algoritmos produjeron exactamente el mismo costo óptimo de viaje y la misma distancia física**, validando que la heurística implementada es admisible ($h(n) \le h^*(n)$) y consistente.

---

## 8. Limitaciones Técnicas Identificadas

- **Modelo de Grafo No Orientado:** La red vial modela vías bidireccionales simétricas. Las calles de sentido único requerirían una representación dirigida (`networkx.DiGraph`).
- **Heurística Euclidiana en Tráfico Severo:** Si una vía sufre una congestión extrema, el tiempo real de viaje puede superar notablemente la estimación en línea recta libre. Aunque la heurística sigue siendo admisible, su poder de orientación disminuye levemente ante condiciones de tráfico atípicas.
- **Topología en Memoria:** El grafo se gestiona directamente en memoria RAM local, lo cual es ideal para tiempos de respuesta submilimétricos en el ámbito académico, pero requeriría persistencia relacional en implementaciones con millones de nodos.

---

## 9. Conclusión

El sistema **TrafficFlow** superó la totalidad de las 18 pruebas automatizadas diseñadas, validando el correcto funcionamiento de su arquitectura modular y la implementación de los patrones de diseño **Strategy** y **Observer**.

Los resultados empíricos demuestran cuantitativamente que la efectividad de A* frente a Dijkstra depende directamente de la topología de la red vial y de la capacidad de la heurística para podar ramas no orientadas al objetivo.
