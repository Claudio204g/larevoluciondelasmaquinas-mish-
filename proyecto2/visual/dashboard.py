import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from model.graph import Graph
from domain.order import OrderStatus
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import time

class DroneDeliveryDashboard:
    def __init__(self):
        self.sim = None
        self.initialize_session_state()
        
        # Configuración de la página
        st.set_page_config(
            page_title="Sistema Logístico con Drones",
            page_icon="🚁",
            layout="wide"
        )
    
    def initialize_session_state(self):
        """Inicializa el estado de la sesión de Streamlit."""
        if 'simulation' not in st.session_state:
            st.session_state.simulation = None
        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = "Run Simulation"
    
    def run(self):
        """Ejecuta la aplicación principal."""
        st.title("🚁 Sistema Logístico Autónomo con Drones")
        
        # Pestañas principales
        tabs = [
            "Run Simulation", 
            "Explore Network", 
            "Clients & Orders",
            "Route Analytics",
            "General Statistics"
        ]
        
        selected_tab = st.sidebar.radio("Navegación", tabs, index=tabs.index(st.session_state.selected_tab))
        st.session_state.selected_tab = selected_tab
        
        if selected_tab == "Run Simulation":
            self.render_run_simulation_tab()
        elif selected_tab == "Explore Network":
            self.render_explore_network_tab()
        elif selected_tab == "Clients & Orders":
            self.render_clients_orders_tab()
        elif selected_tab == "Route Analytics":
            self.render_route_analytics_tab()
        elif selected_tab == "General Statistics":
            self.render_general_stats_tab()
    
    def render_run_simulation_tab(self):
        """Renderiza la pestaña de configuración de simulación."""
        st.header("Configuración de Simulación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            n_nodes = st.slider("Número de nodos", 10, 150, 15)
            m_edges = st.slider("Número de aristas", n_nodes-1, 300, 20)
            n_orders = st.slider("Número de órdenes iniciales", 1, 300, 10)
        
        with col2:
            st.markdown("**Distribución de nodos:**")
            st.markdown("- 20% Almacenamiento")
            st.markdown("- 20% Recarga")
            st.markdown("- 60% Clientes")
            
            st.markdown("**Parámetros de drones:**")
            st.markdown(f"- Autonomía máxima: 50 unidades")
        
        if st.button("Iniciar Simulación", type="primary"):
            initializer = SimulationInitializer()
            graph = initializer.generate_connected_graph(n_nodes, m_edges)
            self.sim = Simulation(graph)
            
            # Generar órdenes iniciales
            for _ in range(n_orders):
                self.sim.generate_random_order()
            
            st.session_state.simulation = self.sim
            st.success("¡Simulación iniciada correctamente!")
            st.rerun()
        
        if st.session_state.simulation:
            st.divider()
            self.show_simulation_status()
    
    def render_explore_network_tab(self):
        """Renderiza la pestaña de exploración de red."""
        if not st.session_state.simulation:
            st.warning("Por favor inicia una simulación primero.")
            return

        self.sim = st.session_state.simulation
        st.header("Exploración de Red")

        st.subheader("Mapa de la Red")
        mostrar_mst = st.checkbox("Mostrar MST (Kruskal)", value=False)
        self.render_network_map(mostrar_mst=mostrar_mst)

        st.subheader("Calcular Ruta")
        self.render_route_calculator()
    
    def render_network_map(self, mostrar_mst=False):
        graph = self.sim.graph
        m = folium.Map(location=[-38.7397, -72.5984], zoom_start=13)

        # Nodos
        for vertex in graph.vertices.values():
            color = self.get_vertex_color(vertex.vertex_type)
            folium.Marker(
                location=vertex.coordinates,
                popup=f"{vertex.id} ({vertex.vertex_type.value})",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)

        # Aristas normales
        for edge in graph.edges:
            src = graph.vertices[edge.source_id]
            dst = graph.vertices[edge.target_id]
            folium.PolyLine(
                locations=[src.coordinates, dst.coordinates],
                color="gray",
                weight=1,
                opacity=0.6
            ).add_to(m)

        # Aristas MST si corresponde
        if mostrar_mst:
            mst_edges = graph.kruskal_mst()
            for edge in mst_edges:
                src = graph.vertices[edge.source_id]
                dst = graph.vertices[edge.target_id]
                folium.PolyLine(
                    locations=[src.coordinates, dst.coordinates],
                    color="blue",
                    weight=3,
                    opacity=0.8,
                    dash_array="5, 5"
                ).add_to(m)

        st_folium(m, width=1200, height=600)
    
    def highlight_route_on_map(self, path):
        graph = self.sim.graph
        m = folium.Map(location=[-38.7397, -72.5984], zoom_start=13)

        # Agregar nodos
        for vertex in graph.vertices.values():
            color = self.get_vertex_color(vertex.vertex_type)
            folium.Marker(
                location=vertex.coordinates,
                popup=f"{vertex.id} ({vertex.vertex_type.value})",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)

        # Agregar ruta destacada
        for i in range(len(path) - 1):
            src = graph.vertices[path[i]]
            dst = graph.vertices[path[i + 1]]
            folium.PolyLine(
                locations=[src.coordinates, dst.coordinates],
                color="red",
                weight=5,
                opacity=0.8
            ).add_to(m)

        st_folium(m, width=1200, height=600)
    
    def get_vertex_color(self, vertex_type):
        """Retorna el color correspondiente al tipo de vértice."""
        colors = {
            "storage": "blue",
            "recharge": "green",
            "client": "orange"
        }
        return colors.get(vertex_type.value, "gray")
    
    def render_route_calculator(self):
        """Renderiza el formulario para calcular rutas."""
        graph = self.sim.graph
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            storage_nodes = [v.id for v in graph.vertices.values() if v.vertex_type.value == "storage"]
            origin_id = st.selectbox("Nodo Origen (Almacenamiento)", storage_nodes)
        
        with col2:
            client_nodes = [v.id for v in graph.vertices.values() if v.vertex_type.value == "client"]
            destination_id = st.selectbox("Nodo Destino (Cliente)", client_nodes)
        
        with col3:
            algorithm = st.radio("Algoritmo", ["Dijkstra", "Floyd-Warshall"])

        # Calcular nueva ruta
        if st.button("Calcular Ruta"):
            try:
                route = self.sim.calculate_route(origin_id, destination_id, algorithm.lower())

                # Guardar la ruta
                st.session_state["last_route"] = route

                st.success("¡Ruta calculada exitosamente!")
                st.markdown(f"**Ruta:** {' → '.join(route.path)}")
                st.markdown(f"**Costo total:** {route.total_cost:.2f}")
                st.markdown(f"**Paradas de recarga:** {route.recharge_stops}")
                
            except Exception as e:
                st.error(f"Error al calcular ruta: {str(e)}")

        # Mostrar ruta si está guardada
        if "last_route" in st.session_state:
            route = st.session_state["last_route"]
            st.info(f"Ruta más reciente: {' → '.join(route.path)}")
            self.highlight_route_on_map(route.path)

            if st.button("Completar Entrega y Crear Orden"):
                try:
                    order = self.sim.generate_random_order()
                    order.origin_id = origin_id
                    order.destination_id = destination_id
                    self.sim.complete_order(order.id, route)
                    st.success(f"Orden {order.id} completada exitosamente!")
                    st.session_state.simulation = self.sim
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al completar la orden: {str(e)}")
    
    def highlight_route_on_map(self, path):
        """Resalta una ruta específica en el mapa."""
        graph = self.sim.graph
        
        m = folium.Map(location=[-38.7397, -72.5984], zoom_start=13)
        
        # Añadir todos los nodos
        for vertex in graph.vertices.values():
            color = self.get_vertex_color(vertex.vertex_type)
            folium.Marker(
                location=vertex.coordinates,
                popup=f"{vertex.id} ({vertex.vertex_type.value})",
                icon=folium.Icon(color=color, icon="circle")
            ).add_to(m)
        
        # Resaltar ruta
        for i in range(len(path) - 1):
            source = graph.vertices[path[i]]
            target = graph.vertices[path[i+1]]
            folium.PolyLine(
                locations=[source.coordinates, target.coordinates],
                color='red',
                weight=3,
                opacity=1
            ).add_to(m)
        
        st_folium(m, width=1200, height=600)
    
    def render_minimum_spanning_tree(self):
        """Muestra el árbol de expansión mínima."""
        graph = self.sim.graph
        mst_edges = graph.kruskal_mst()
        
        m = folium.Map(location=[-38.7397, -72.5984], zoom_start=13)
        
        # Añadir nodos
        for vertex in graph.vertices.values():
            color = self.get_vertex_color(vertex.vertex_type)
            folium.Marker(
                location=vertex.coordinates,
                popup=f"{vertex.id} ({vertex.vertex_type.value})",
                icon=folium.Icon(color=color, icon="circle")
            ).add_to(m)
        
        # Añadir aristas del MST
        for edge in mst_edges:
            source = graph.vertices[edge.source_id]
            target = graph.vertices[edge.target_id]
            folium.PolyLine(
                locations=[source.coordinates, target.coordinates],
                color='blue',
                weight=2,
                opacity=0.7,
                dash_array='5, 5'
            ).add_to(m)
        
        st_folium(m, width=1200, height=600)
    
    def render_clients_orders_tab(self):
        """Renderiza la pestaña de clientes y órdenes."""
        if not st.session_state.simulation:
            st.warning("Por favor inicia una simulación primero.")
            return
        
        self.sim = st.session_state.simulation
        st.header("Clientes y Órdenes")
        
        # Mostrar clientes
        st.subheader("Lista de Clientes")
        clients_data = []
        for client_id, client in self.sim.clients.items():
            clients_data.append([
                client_id,
                client.name,
                client.client_type,
                client.total_orders,
                client.coordinates
            ])
        
        clients_df = pd.DataFrame(
            clients_data,
            columns=["ID", "Nombre", "Tipo", "Pedidos", "Coordenadas"]
        )
        st.dataframe(clients_df, hide_index=True)
        
        # Mostrar órdenes
        st.subheader("Historial de Órdenes")
        orders_data = []
        for order_id, order in self.sim.orders.items():
            orders_data.append([
                order_id,
                order.client_id,
                order.origin_id,
                order.destination_id,
                order.status.value,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.completed_at.strftime("%Y-%m-%d %H:%M") if order.completed_at else "N/A",
                order.priority,
                order.energy_cost or "N/A"
            ])
        
        orders_df = pd.DataFrame(
            orders_data,
            columns=["ID", "Cliente", "Origen", "Destino", "Estado", 
                    "Creada", "Completada", "Prioridad", "Costo Energía"]
        )
        st.dataframe(orders_df, hide_index=True)
    
    def render_route_analytics_tab(self):
        """Renderiza la pestaña de análisis de rutas."""
        if not st.session_state.simulation:
            st.warning("Por favor inicia una simulación primero.")
            return

        self.sim = st.session_state.simulation
        st.header("Análisis de Rutas")

        # Mostrar rutas más frecuentes
        st.subheader("Rutas Más Frecuentes")
        if hasattr(self.sim, 'avl_routes') and self.sim.avl_routes:
            frequent_routes = self.sim.avl_routes.get_most_frequent(10)

            routes_data = []
            for route in frequent_routes:
                routes_data.append([
                    route.key,
                    route.value
                ])

            routes_df = pd.DataFrame(
                routes_data,
                columns=["Ruta", "Frecuencia"]
            )
            st.dataframe(routes_df, hide_index=True)

            # Visualización con gráfico de barras
            st.subheader("Gráfico de Frecuencia de Rutas")
            ruta_labels = [r.key for r in frequent_routes]
            frecuencias = [r.value for r in frequent_routes]

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(ruta_labels, frecuencias, color='orange')
            ax.set_title("Top Rutas Frecuentes")
            ax.set_ylabel("Frecuencia")
            ax.set_xlabel("Ruta")
            plt.xticks(rotation=30, ha='right')

            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 0.3, int(yval), ha='center', va='bottom')

            st.pyplot(fig)

            # Visualización del árbol AVL
            st.subheader("Visualización del Árbol AVL")
            self.render_avl_visualization()

            # Generar informe PDF
            st.subheader("Generar Informe")
            if st.button("Generar Informe PDF"):
                pdf_path = self.generate_pdf_report()

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="Descargar Informe",
                        data=f,
                        file_name="informe_rutas.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("No hay datos de rutas disponibles. Calcula algunas rutas primero.")

    def render_avl_visualization(self):
        """Visualiza el árbol AVL usando NetworkX y Matplotlib (sin pygraphviz)."""
        if not hasattr(self.sim, 'avl_routes') or not self.sim.avl_routes:
            return

        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()

        def add_nodes_edges(node, parent=None):
            if node:
                label = f"{node.key[:15]}...\n{node.value}" if len(node.key) > 15 else f"{node.key}\n{node.value}"
                G.add_node(node.key, label=label)
                if parent:
                    G.add_edge(parent.key, node.key)
                add_nodes_edges(node.left, node)
                add_nodes_edges(node.right, node)

        add_nodes_edges(self.sim.avl_routes.root)

        labels = nx.get_node_attributes(G, 'label')
        pos = nx.spring_layout(G, seed=42)  # Sin pygraphviz
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=2500, node_color='skyblue',
                font_size=8, font_weight='bold', arrows=True)
        plt.title("Árbol AVL de Rutas Frecuentes")
        st.pyplot(plt)
    
    def generate_pdf_report(self):
        """Genera un informe PDF con las estadísticas del sistema."""
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        elements.append(Paragraph("Informe de Rutas - Sistema de Drones", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Datos básicos
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Rutas más frecuentes
        elements.append(Paragraph("Rutas Más Frecuentes", styles['Heading2']))
        
        frequent_routes = self.sim.avl_routes.get_most_frequent(10)
        routes_data = [["Ruta", "Frecuencia"]]
        for route in frequent_routes:
            routes_data.append([route.key, str(route.value)])
        
        routes_table = Table(routes_data)
        routes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(routes_table)
        elements.append(Spacer(1, 24))
        
        # Estadísticas generales
        elements.append(Paragraph("Estadísticas Generales", styles['Heading2']))
        
        stats = self.sim.get_simulation_stats()
        stats_data = [
            ["Nodos totales", stats['total_nodes']],
            ["Aristas totales", stats['total_edges']],
            ["Clientes registrados", stats['total_clients']],
            ["Órdenes totales", stats['total_orders']],
            ["Órdenes completadas", stats['completed_orders']],
            ["Órdenes pendientes", stats['pending_orders']]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        
        # Guardar PDF en un archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        doc.build(elements)
        
        return temp_file.name
    
    def render_general_stats_tab(self):
        """Renderiza la pestaña de estadísticas generales."""
        if not st.session_state.simulation:
            st.warning("Por favor inicia una simulación primero.")
            return
        
        self.sim = st.session_state.simulation
        st.header("Estadísticas Generales")
        
        # Mostrar estadísticas clave
        stats = self.sim.get_simulation_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nodos totales", stats['total_nodes'])
            st.metric("Aristas totales", stats['total_edges'])
        
        with col2:
            st.metric("Clientes registrados", stats['total_clients'])
            st.metric("Órdenes totales", stats['total_orders'])
        
        with col3:
            st.metric("Órdenes completadas", stats['completed_orders'])
            st.metric("Órdenes pendientes", stats['pending_orders'])
        
        # Gráfico de distribución de nodos
        st.subheader("Distribución de Nodos")
        node_types = {
            "Almacenamiento": len([v for v in self.sim.graph.vertices.values() 
                                 if v.vertex_type.value == "storage"]),
            "Recarga": len([v for v in self.sim.graph.vertices.values() 
                          if v.vertex_type.value == "recharge"]),
            "Cliente": len([v for v in self.sim.graph.vertices.values() 
                          if v.vertex_type.value == "client"])
        }
        
        fig, ax = plt.subplots()
        ax.pie(node_types.values(), labels=node_types.keys(), autopct='%1.1f%%')
        ax.set_title("Distribución de Tipos de Nodos")
        st.pyplot(fig)
    
    def show_simulation_status(self):
        """Muestra el estado actual de la simulación."""
        if 'simulation' not in st.session_state or st.session_state.simulation is None:
            st.warning("No hay simulación activa.")
            return

        self.sim = st.session_state.simulation  # ✅ Refresca la referencia

        st.subheader("Estado de la Simulación")

        stats = self.sim.get_simulation_stats()

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"Nodos: {stats['total_nodes']}")
            st.write(f"Aristas: {stats['total_edges']}")
            st.write(f"Clientes: {stats['total_clients']}")

        with col2:
            st.write(f"Órdenes: {stats['total_orders']}")
            st.write(f"Completadas: {stats['completed_orders']}")
            st.write(f"Última actualización: {stats['timestamp']}")

# Punto de entrada de la aplicación
if __name__ == "__main__":
    dashboard = DroneDeliveryDashboard()
    dashboard.run()