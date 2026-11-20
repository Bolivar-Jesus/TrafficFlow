import matplotlib.pyplot as plt
import streamlit as st
from trafficflow.algorithms import (
    AStarStrategy,
    DijkstraStrategy,
    RoutePlanner,
    RouteResult,
)
from trafficflow.graph import CityGraph, create_default_city
from trafficflow.metrics import compare_strategies
from trafficflow.traffic import RouteStateObserver, TrafficManager

st.set_page_config(
    page_title="TrafficFlow — Simulador de Rutas Urbanas",
    page_icon="🚦",
    layout="wide",
)


def get_system_state():
    if "city" not in st.session_state:
        st.session_state.city = create_default_city()
        st.session_state.traffic_mgr = TrafficManager(st.session_state.city)
        st.session_state.observer = RouteStateObserver()
        st.session_state.traffic_mgr.attach(st.session_state.observer)
        st.session_state.planner = RoutePlanner(DijkstraStrategy())
        st.session_state.last_route = None
        st.session_state.last_comparison = None
        st.session_state.selected_origin = "N1"
        st.session_state.selected_dest = "N16"
    return (
        st.session_state.city,
        st.session_state.traffic_mgr,
        st.session_state.observer,
        st.session_state.planner,
    )


city, traffic_mgr, observer, planner = get_system_state()


def render_city_map(
    graph: CityGraph,
    active_path: list[str] = None,
    origin: str = None,
    destination: str = None,
):
    fig, ax = plt.subplots(figsize=(10, 6.8), dpi=100)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    nodes = graph.get_nodes()
    pos = {nid: (node.x, node.y) for nid, node in nodes.items()}

    # Set de segmentos de la ruta activa
    route_edges = set()
    if active_path and len(active_path) > 1:
        for i in range(len(active_path) - 1):
            u, v = active_path[i], active_path[i + 1]
            route_edges.add(tuple(sorted((u, v))))

    # Dibujar aristas según su estado
    for edge in graph.get_edges():
        pair = tuple(sorted((edge.u, edge.v)))
        x_vals = [pos[edge.u][0], pos[edge.v][0]]
        y_vals = [pos[edge.u][1], pos[edge.v][1]]
        mid_x = sum(x_vals) / 2.0
        mid_y = sum(y_vals) / 2.0

        if edge.is_closed:
            ax.plot(
                x_vals,
                y_vals,
                color="#dc2626",
                linestyle="--",
                linewidth=2.5,
                alpha=0.85,
                zorder=2,
            )
            ax.text(
                mid_x,
                mid_y,
                "⛔ CERRADA",
                fontsize=8,
                fontweight="bold",
                color="#991b1b",
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="#fee2e2",
                    edgecolor="#dc2626",
                    alpha=0.9,
                ),
                zorder=6,
            )
        elif edge.congestion_factor > 1.0:
            ax.plot(
                x_vals,
                y_vals,
                color="#ea580c",
                linestyle="-",
                linewidth=3.5,
                alpha=0.9,
                zorder=3,
            )
            ax.text(
                mid_x,
                mid_y,
                f"x{edge.congestion_factor:.1f}",
                fontsize=8,
                fontweight="bold",
                color="#c2410c",
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="#ffedd5",
                    edgecolor="#ea580c",
                    alpha=0.9,
                ),
                zorder=6,
            )
        else:
            ax.plot(
                x_vals,
                y_vals,
                color="#94a3b8",
                linestyle="-",
                linewidth=2.0,
                alpha=0.75,
                zorder=1,
            )

    # Dibujar ruta activa sobrepuesta
    if active_path and len(active_path) > 1:
        for i in range(len(active_path) - 1):
            u, v = active_path[i], active_path[i + 1]
            x_vals = [pos[u][0], pos[v][0]]
            y_vals = [pos[u][1], pos[v][1]]
            ax.plot(
                x_vals,
                y_vals,
                color="#059669",
                linestyle="-",
                linewidth=5.5,
                alpha=0.9,
                zorder=4,
            )

    # Dibujar nodos
    for nid, node in nodes.items():
        x, y = node.x, node.y
        if nid == origin:
            node_color = "#2563eb"
            border_color = "#1d4ed8"
            size = 520
        elif nid == destination:
            node_color = "#7c3aed"
            border_color = "#6d28d9"
            size = 520
        elif active_path and nid in active_path:
            node_color = "#10b981"
            border_color = "#047857"
            size = 460
        else:
            node_color = "#ffffff"
            border_color = "#475569"
            size = 380

        ax.scatter(
            [x],
            [y],
            s=size,
            color=node_color,
            edgecolors=border_color,
            linewidths=2.2,
            zorder=7,
        )
        label_text = f"{nid}\n{node.name}"
        ax.text(
            x,
            y,
            nid,
            fontsize=9,
            fontweight="bold",
            color="#ffffff"
            if (nid in [origin, destination] or (active_path and nid in active_path))
            else "#1e293b",
            ha="center",
            va="center",
            zorder=8,
        )
        ax.text(
            x,
            y - 0.28,
            node.name,
            fontsize=7.5,
            color="#334155",
            ha="center",
            va="top",
            zorder=8,
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="#ffffff",
                edgecolor="none",
                alpha=0.75,
            ),
        )

    # Margen y aspecto
    ax.set_aspect("equal", adjustable="datalim")
    ax.margins(0.12)
    ax.axis("off")
    ax.set_title(
        f"Red Vial — {graph.name}",
        fontsize=13,
        fontweight="bold",
        pad=12,
        color="#0f172a",
    )
    plt.tight_layout()
    return fig


# --- Barra lateral ---
st.sidebar.title("🚦 Control de Navegación")

node_options = {f"{nid} - {node.name}": nid for nid, node in city.get_nodes().items()}
node_keys = list(node_options.keys())

default_orig_idx = 0
default_dest_idx = len(node_keys) - 1

origin_label = st.sidebar.selectbox(
    "Intersección de Origen:", node_keys, index=default_orig_idx
)
dest_label = st.sidebar.selectbox(
    "Intersección de Destino:", node_keys, index=default_dest_idx
)

origin_id = node_options[origin_label]
dest_id = node_options[dest_label]

algorithm_choice = st.sidebar.radio(
    "Algoritmo de búsqueda (Strategy):",
    ["Dijkstra", "A*"],
    help="Dijkstra explora exhaustivamente por costo. A* utiliza una heurística euclidiana admisible.",
)

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    btn_calculate = st.button("Calcular Ruta", use_container_width=True, type="primary")
with col_btn2:
    btn_compare = st.button("Comparar Algoritmos", use_container_width=True)

st.sidebar.divider()
st.sidebar.subheader("🚗 Gestión de Tráfico (Observer)")

all_edges = city.get_edges()
edge_options = {}
for e in all_edges:
    key = f"{e.u} ↔ {e.v} ({e.distance:.1f} km)"
    edge_options[key] = (e.u, e.v)

selected_edge_key = st.sidebar.selectbox("Seleccionar vía:", list(edge_options.keys()))
sel_u, sel_v = edge_options[selected_edge_key]

congestion_val = st.sidebar.slider(
    "Factor de congestión:", min_value=1.0, max_value=5.0, value=2.0, step=0.5
)

col_t1, col_t2 = st.sidebar.columns(2)
with col_t1:
    if st.button("Aplicar Congestión", use_container_width=True):
        traffic_mgr.apply_congestion(sel_u, sel_v, congestion_val)
        st.session_state.last_comparison = None
        if st.session_state.last_route and st.session_state.last_route.success:
            st.session_state.last_route = planner.calculate_route(
                city, origin_id, dest_id
            )
        st.rerun()

with col_t2:
    current_edge = city.get_edge(sel_u, sel_v)
    is_currently_closed = current_edge.is_closed if current_edge else False
    if is_currently_closed:
        if st.button("Reabrir Vía", use_container_width=True):
            traffic_mgr.reopen_road(sel_u, sel_v)
            st.session_state.last_comparison = None
            st.rerun()
    else:
        if st.button("Cerrar Vía", use_container_width=True):
            traffic_mgr.close_road(sel_u, sel_v)
            st.session_state.last_comparison = None
            st.rerun()

if st.sidebar.button("Restablecer Mapa", use_container_width=True):
    traffic_mgr.reset_all()
    st.session_state.last_route = None
    st.session_state.last_comparison = None
    st.rerun()

# Estado activo de modificaciones
active_congestions = traffic_mgr.get_active_congestions()
active_closures = traffic_mgr.get_closed_roads()

if active_congestions or active_closures:
    st.sidebar.caption("Condiciones viales modificadas:")
    for cu, cv, factor in active_congestions:
        st.sidebar.markdown(f"• 🟡 **{cu} ↔ {cv}**: Congestión x{factor:.1f}")
    for cu, cv in active_closures:
        st.sidebar.markdown(f"• 🔴 **{cu} ↔ {cv}**: Vía cerrada")

# --- Contenido Principal ---
st.title("TrafficFlow — Simulador de Rutas Urbanas")
st.markdown(
    "Evaluación y optimización de rutas urbanas mediante los algoritmos **Dijkstra** y **A\\***, "
    "incorporando simulación de congestión vehicular y cierres temporales de vías."
)

if btn_calculate:
    if algorithm_choice == "Dijkstra":
        planner.set_strategy(DijkstraStrategy())
    else:
        planner.set_strategy(AStarStrategy())

    st.session_state.last_route = planner.calculate_route(city, origin_id, dest_id)
    st.session_state.last_comparison = None

if btn_compare:
    st.session_state.last_comparison = compare_strategies(city, origin_id, dest_id)
    st.session_state.last_route = None

# Renderizar Mapa
active_path = None
if st.session_state.last_route and st.session_state.last_route.success:
    active_path = st.session_state.last_route.path
elif st.session_state.last_comparison:
    # Tomar la ruta calculada por la primera estrategia exitosa
    for item in st.session_state.last_comparison.values():
        if item.success:
            active_path = item.path
            break

map_fig = render_city_map(
    city,
    active_path=active_path,
    origin=origin_id,
    destination=dest_id,
)
st.pyplot(map_fig)
plt.close(map_fig)

# Leyenda visual
st.markdown(
    """
    <div style="display: flex; gap: 24px; flex-wrap: wrap; background-color: #f1f5f9; padding: 10px 16px; border-radius: 8px; margin-bottom: 20px; font-size: 0.88rem;">
      <span>🔵 <b>Origen</b></span>
      <span>🟣 <b>Destino</b></span>
      <span>🟢 <b>Ruta activa</b></span>
      <span>⚪ <b>Vía normal</b></span>
      <span>🟠 <b>Vía congestionada</b></span>
      <span>🔴 <b>Vía cerrada</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Resultados de Ruta Individual
if st.session_state.last_route:
    res = st.session_state.last_route
    st.subheader(f"Resultado de Navegación — {res.algorithm}")

    if res.success:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distancia Total", f"{res.total_distance:.2f} km")
        c2.metric("Tiempo de Viaje Estimado", f"{res.total_time:.2f} min")
        c3.metric("Tiempo de Cómputo", f"{res.execution_time_ms:.3f} ms")
        c4.metric("Nodos Explorados", f"{res.nodes_explored}")

        path_names = [f"{nid} ({city.get_node(nid).name})" for nid in res.path]
        st.success(f"**Ruta encontrada:** {' ➔ '.join(path_names)}")
    else:
        st.warning(f"⚠️ {res.message}")

# Resultados de Comparación
if st.session_state.last_comparison:
    st.subheader("Comparación de Algoritmos (Dijkstra vs A*)")
    comp = st.session_state.last_comparison

    d_res = comp.get("Dijkstra")
    a_res = comp.get("A*")

    if d_res and a_res and d_res.success and a_res.success:
        col_d, col_a = st.columns(2)

        with col_d:
            st.markdown("### Algoritmo Dijkstra")
            st.metric("Tiempo Estimado de Viaje", f"{d_res.travel_time_min:.2f} min")
            st.metric("Distancia Total", f"{d_res.distance_km:.2f} km")
            st.metric("Tiempo de Ejecución", f"{d_res.execution_time_ms:.4f} ms")
            st.metric("Nodos Explorados", f"{d_res.nodes_explored}")
            st.caption(f"**Ruta:** {d_res.path_str}")

        with col_a:
            st.markdown("### Algoritmo A*")
            st.metric("Tiempo Estimado de Viaje", f"{a_res.travel_time_min:.2f} min")
            st.metric("Distancia Total", f"{a_res.distance_km:.2f} km")
            st.metric("Tiempo de Ejecución", f"{a_res.execution_time_ms:.4f} ms")
            st.metric("Nodos Explorados", f"{a_res.nodes_explored}")
            st.caption(f"**Ruta:** {a_res.path_str}")

        st.info(
            f"**Análisis comparativo:** Ambos algoritmos alcanzaron el tiempo óptimo de viaje de "
            f"**{d_res.travel_time_min:.2f} min** sobre una distancia física de **{d_res.distance_km:.2f} km**. "
            f"En exploración de nodos, A* exploró **{a_res.nodes_explored}** frente a **{d_res.nodes_explored}** de Dijkstra."
        )
    else:
        st.warning("No se pudo completar la comparación debido a falta de conectividad entre los puntos.")
