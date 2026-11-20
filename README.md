# TrafficFlow — Simulador de Rutas Urbanas

Aplicación interactiva para la modelación, evaluación y optimización de algoritmos de navegación urbana bajo condiciones dinámicas de tráfico.

---

## 1. Nombre del Proyecto
**TrafficFlow — Simulador de Rutas Urbanas**

---

## 2. Descripción General
**TrafficFlow** es una aplicación desarrollada en Python 3.12 y Streamlit que representa una ciudad simulada mediante un grafo ponderado de intersecciones y vías. El sistema permite planificar rutas óptimas entre cualquier par de puntos utilizando los algoritmos **Dijkstra** y **A\***, analizar el impacto de congestiones vehiculares y cierres temporales de vías, y comparar cuantitativamente el desempeño de ambas estrategias de navegación mediante métricas reales de ejecución y exploración.

---

## 3. Objetivo
Proporcionar una herramienta visual y analítica para la evaluación y optimización de arquitecturas de software y algoritmos de grafos en entornos urbanos, facilitando el análisis comparativo del tiempo de cómputo, número de nodos explorados y tiempo de viaje ante condiciones variables de la red vial.

---

## 4. Funcionalidades Implementadas

- **Mapa Urbano Interactivo:**
  - Modelación de la red vial mediante un grafo donde los nodos representan intersecciones con coordenadas espaciales y las aristas representan vías con longitud física y velocidad de diseño.
  - Representación gráfica de la red con diferenciación clara de vías normales, congestionadas y cerradas.
  - Selección de puntos de origen y destino desde selectores integrados.
  - Resaltado visual del trazado de la ruta calculada sobre el mapa.
- **Cálculo de Rutas Óptimas:**
  - Implementación del algoritmo **Dijkstra** para búsqueda de camino de menor costo.
  - Implementación del algoritmo **A\*** con heurística euclidiana admisible basada en la velocidad máxima de la red.
- **Simulación Dinámica de Tráfico:**
  - Aplicación de factores de congestión (1.0x a 5.0x) sobre vías específicas, aumentando el tiempo estimado de viaje sin alterar la distancia física.
  - Cierre y reapertura temporal de vías, obligando a los algoritmos a calcular desvíos viables.
  - Restablecimiento completo de la red a sus condiciones originales con un solo clic.
  - Manejo seguro de casos sin conexión vial disponible, informando al usuario sin provocar fallos en el sistema.
- **Comparación y Métricas de Rendimiento:**
  - Comparativa directa entre Dijkstra y A* bajo exactamente las mismas condiciones viales.
  - Medición y presentación de métricas reales: distancia física (km), tiempo estimado de viaje (min), tiempo de ejecución del algoritmo (ms) y nodos explorados.
  - Distinción explícita entre tiempo de viaje en la ciudad y tiempo de cómputo del algoritmo.

---

## 5. Tecnologías Utilizadas

- **Python 3.12:** Lenguaje principal de programación.
- **Streamlit:** Framework para la construcción de la interfaz gráfica web interactiva.
- **NetworkX:** Modelación y manipulación de estructuras de grafos.
- **Matplotlib:** Renderizado y dibujo vectorial de la red urbana y las rutas.
- **Pytest:** Framework de pruebas automatizadas y benchmarking.
- **PlantUML:** Generación y especificación formal de diagramas UML de arquitectura.

---

## 6. Arquitectura del Sistema

El sistema implementa una arquitectura modular de capas desacopladas:

1. **Capa de Dominio y Red Vial (`trafficflow/graph.py`):** Modela las entidades fundamentales (`CityNode`, `CityEdge`, `CityGraph`), gestionando la topología de la ciudad, distancias euclidianas y costos de recorrido.
2. **Capa de Algoritmos de Navegación (`trafficflow/algorithms.py`):** Encapsula los motores de búsqueda mediante el patrón **Strategy**, permitiendo el intercambio dinámico de algoritmos de navegación.
3. **Capa de Control de Tráfico (`trafficflow/traffic.py`):** Administra los eventos viales (congestiones, cierres, restablecimientos) aplicando el patrón **Observer** para notificar reactivamente los cambios.
4. **Capa de Evaluación y Métricas (`trafficflow/metrics.py`):** Ejecuta análisis comparativos y pruebas de benchmarking sobre la red.
5. **Capa de Presentación (`app.py`):** Interfaz de usuario interactiva desarrollada con Streamlit y renderizado con Matplotlib.

---

## 7. Patrones de Diseño Aplicados

### Patrón Strategy
- **Propósito:** Desacoplar la lógica de selección de ruta de la implementación específica de cada algoritmo de búsqueda.
- **Estructura:**
  - `RouteStrategy` (interfaz abstracta): Declara el método `find_route(graph, origin, destination) -> RouteResult`.
  - `DijkstraStrategy` y `AStarStrategy` (estrategias concretas): Implementaciones especializadas de búsqueda.
  - `RoutePlanner` (contexto): Mantiene una referencia a la estrategia activa y permite cambiarla en tiempo de ejecución (`set_strategy`) sin modificar la interfaz de usuario ni la estructura del grafo.

### Patrón Observer
- **Propósito:** Notificar a los componentes interesados cuando ocurren cambios en las condiciones viales (aplicación de congestión, cierre o restablecimiento) para invalidar rutas calculadas previamente y actualizar la visualización.
- **Estructura:**
  - `TrafficObserver` (interfaz abstracta): Declara el método `on_traffic_changed(event: TrafficEvent)`.
  - `TrafficSubject` (sujeto abstracto): Métodos `attach`, `detach` y `notify`.
  - `TrafficManager` (sujeto concreto): Administra el estado de la red y emite eventos viales tipificados (`TrafficEventType`).
  - `RouteStateObserver` (observador concreto): Registra eventos y actualiza el estado de invalidación de ruta.

---

## 8. Estructura de Carpetas

```text
TrafficFlow/
├── app.py                     # Interfaz web principal (Streamlit)
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación integral del sistema
├── trafficflow/               # Paquete modular del núcleo
│   ├── __init__.py            # Exportaciones públicas del paquete
│   ├── graph.py               # Modelo de grafo, nodos, aristas y generador de ciudad
│   ├── algorithms.py          # Patrón Strategy (Dijkstra, A*, RoutePlanner)
│   ├── traffic.py             # Patrón Observer (TrafficManager, eventos y observadores)
│   └── metrics.py             # Motor de métricas comparativas y benchmarks
├── diagrams/                  # Diagramas de arquitectura en PlantUML
│   ├── componentes.puml       # Código fuente del diagrama de componentes
│   ├── componentes.png        # Imagen renderizada del diagrama de componentes
│   ├── clases.puml            # Código fuente del diagrama de clases
│   ├── clases.png             # Imagen renderizada del diagrama de clases
│   ├── secuencia.puml          # Código fuente del diagrama de secuencia
│   ├── secuencia.png          # Imagen renderizada del diagrama de secuencia
│   ├── actividades.puml        # Código fuente del diagrama de actividades
│   └── actividades.png        # Imagen renderizada del diagrama de actividades
├── tests/                     # Suite de pruebas automatizadas
│   ├── __init__.py
│   ├── test_algorithms.py     # Pruebas de Dijkstra, A*,Optimalidad y Strategy
│   ├── test_traffic.py        # Pruebas de congestión, cierres, reset y Observer
│   ├── test_metrics.py        # Pruebas de cálculo de distancias, tiempos y métricas
│   └── test_benchmarks.py     # Pruebas de rendimiento en múltiples tamaños de red
└── docs/                      # Documentación y reportes técnicos
    └── resultados_pruebas.md  # Informe formal de pruebas y benchmarking
```

---

## 9. Requisitos Previos

- **Sistema Operativo:** Windows 11 (o compatible).
- **Python:** Versión 3.11 o superior (verificado en Python 3.12.4).
- **Gestor de paquetes:** `pip` actualizado.

---

## 10. Instalación de Dependencias

1. Abra una terminal de PowerShell en la carpeta raíz del proyecto (`TrafficFlow`):
   ```powershell
   cd c:\Users\jesus\Documents\Ingeniería\TrafficFlow
   ```

2. Instale las dependencias requeridas mediante el archivo `requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 11. Instrucciones de Ejecución

Para iniciar la aplicación gráfica interactiva en su navegador:

```powershell
streamlit run app.py
```

La aplicación se abrirá automáticamente en su navegador predeterminado en la dirección local:
`http://localhost:8501`

---

## 12. Instrucciones para Ejecutar las Pruebas

Para ejecutar la suite completa de pruebas automatizadas:

```powershell
pytest -v
```

Para ejecutar únicamente las pruebas de rendimiento y benchmarking:

```powershell
pytest tests/test_benchmarks.py -v
```

---

## 13. Descripción de los Diagramas UML

Los diagramas están almacenados en la carpeta `diagrams/` en formato de código editable PlantUML (`.puml`) y en imágenes renderizadas (`.png`):

1. **`componentes.puml` / `componentes.png`:** Representa la interacción modular entre la capa de presentación (Streamlit), el motor de navegación, la gestión de la red vial (NetworkX), la gestión de tráfico y el subsistema de métricas.
2. **`clases.puml` / `clases.png`:** Modela las clases principales del sistema, sus atributos y relaciones, reflejando formalmente la estructura de los patrones de diseño **Strategy** (`RouteStrategy`, `DijkstraStrategy`, `AStarStrategy`, `RoutePlanner`) y **Observer** (`TrafficSubject`, `TrafficManager`, `TrafficObserver`, `RouteStateObserver`).
3. **`secuencia.puml` / `secuencia.png`:** Detalla el flujo cronológico de mensajes desde que el usuario altera el tráfico o solicita el cálculo de una ruta hasta que el resultado es procesado y renderizado en pantalla.
4. **`actividades.puml` / `actividades.png`:** Describe el flujo de control del usuario, abarcando la selección de nodos, configuración de tráfico, bifurcaciones de cálculo o comparación, evaluación de disponibilidad de caminos y visualización.

---

## 14. Resultados Generales de las Pruebas

- **Total de pruebas ejecutadas:** 18
- **Pruebas aprobadas:** 18 (100%)
- **Pruebas fallidas:** 0
- **Tiempo de ejecución:** 1.87 segundos
- **Optimalidad:** Dijkstra y A* obtuvieron exactamente el mismo costo óptimo en todos los escenarios evaluados.
- **Exploración:** En redes urbanas irregulares, A* redujo los nodos explorados en hasta un **72.7%** respecto a Dijkstra, logrando tiempos de cómputo un **39% menores**. En cuadrículas homogéneas simétricas, ambos exploran áreas similares, con una ligera ventaja de CPU para Dijkstra debido a la ausencia de cómputo heurístico.

Para un desglose completo de mediciones y gráficos de desempeño, consulte el documento:
`docs/resultados_pruebas.md`.

---

## 15. Limitaciones Técnicas Reales

1. **Direccionalidad Simétrica:** La red vial modela vías bidireccionales con costos equivalentes en ambos sentidos. Las calles con sentido único requerirían transformar el modelo subyacente a un grafo dirigido (`DiGraph`).
2. **Topología en Memoria:** Los grafos urbanos se instancian y procesan completamente en la memoria de la aplicación, lo que optimiza la velocidad pero limita la escala a redes de hasta decenas de miles de nodos.
3. **Heurística bajo Congestión Extrema:** La heurística euclidiana se basa en la velocidad máxima de diseño en flujo libre. Ante congestiones severas en tramos clave, la heurística continúa siendo admisible pero su capacidad de poda direccional se reduce levemente.
