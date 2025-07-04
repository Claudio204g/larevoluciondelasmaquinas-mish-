import random
from typing import Tuple
from model.graph import Graph
from model.vertex import Vertex, VertexType
from model.edge import Edge

class SimulationInitializer:
    """
    Clase para inicializar simulaciones con grafos conexos y distribución de nodos según requerimientos.
    """
    
    def __init__(self):
        self.min_distance = 0.001  # Distancia mínima entre nodos (aprox. 100m)
        self.max_distance = 0.1    # Distancia máxima entre nodos (aprox. 10km)
        self.center_coords = (-38.7397, -72.5984)  # Coordenadas de Temuco
        self.recharge_visits = {}  # key = node_id, value = visitas
        self.storage_visits = {}
    
    def generate_random_coords(self) -> Tuple[float, float]:
        """Genera coordenadas aleatorias cerca del centro (Temuco)."""
        lat = self.center_coords[0] + random.uniform(-0.1, 0.1)
        lng = self.center_coords[1] + random.uniform(-0.1, 0.1)
        return (lat, lng)
    
    def calculate_distance(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """Calcula distancia aproximada entre dos coordenadas (simplificado)."""
        return ((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2)**0.5
    
    def assign_vertex_type(self, index: int, total: int) -> VertexType:
        """Asigna tipo de nodo según proporciones 20% almacenamiento, 20% recarga, 60% cliente."""
        storage_limit = int(total * 0.2)
        recharge_limit = storage_limit * 2
        
        if index < storage_limit:
            return VertexType.STORAGE
        elif index < recharge_limit:
            return VertexType.RECHARGE
        else:
            return VertexType.CLIENT
    
    def generate_connected_graph(self, n_nodes: int, m_edges: int) -> Graph:
        """
        Genera un grafo conexo aleatorio con:
        - n_nodes vértices (20% almacenamiento, 20% recarga, 60% clientes)
        - m_edges aristas (conexiones) con pesos aleatorios
        - Garantiza que el grafo sea conexo
        """
        if n_nodes < 1:
            raise ValueError("El grafo debe tener al menos 1 nodo")
        if m_edges < n_nodes - 1:
            raise ValueError(f"Para {n_nodes} nodos se necesitan al menos {n_nodes-1} aristas para conexidad")
        
        graph = Graph()
        
        # 1. Crear todos los nodos
        nodes = []
        for i in range(n_nodes):
            node_id = f"node_{i}"
            coords = self.generate_random_coords()
            node_type = self.assign_vertex_type(i, n_nodes)
            
            # Nodos de recarga tienen energía disponible
            energy = random.uniform(50, 100) if node_type == VertexType.RECHARGE else 0
            
            vertex = Vertex(
                id=node_id,
                vertex_type=node_type,
                coordinates=coords,
                name=f"{node_type.value.capitalize()} {i}",
                energy_available=energy
            )
            graph.add_vertex(vertex)
            nodes.append(node_id)
        
        # 2. Conectar todos los nodos en un árbol (garantiza conexidad)
        connected = set([nodes[0]])
        unconnected = set(nodes[1:])
        
        while unconnected:
            src = random.choice(list(connected))
            dst = random.choice(list(unconnected))
            
            src_coords = graph.vertices[src].coordinates
            dst_coords = graph.vertices[dst].coordinates
            distance = self.calculate_distance(src_coords, dst_coords)
            weight = distance * random.uniform(0.8, 1.2)  # Variación aleatoria
            
            edge = Edge(
                source_id=src,
                target_id=dst,
                weight=weight
            )
            graph.add_edge(edge)
            
            connected.add(dst)
            unconnected.remove(dst)
        
        # 3. Añadir aristas adicionales hasta alcanzar m_edges
        existing_edges = {(e.source_id, e.target_id) for e in graph.edges}
        existing_edges.update({(e.target_id, e.source_id) for e in graph.edges})
        
        possible_edges = []
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if (nodes[i], nodes[j]) not in existing_edges:
                    possible_edges.append((nodes[i], nodes[j]))
        
        random.shuffle(possible_edges)
        edges_to_add = min(m_edges - (n_nodes - 1), len(possible_edges))
        
        for i in range(edges_to_add):
            src, dst = possible_edges[i]
            src_coords = graph.vertices[src].coordinates
            dst_coords = graph.vertices[dst].coordinates
            distance = self.calculate_distance(src_coords, dst_coords)
            weight = distance * random.uniform(0.8, 1.2)
            
            edge = Edge(
                source_id=src,
                target_id=dst,
                weight=weight
            )
            graph.add_edge(edge)
        
        return graph

    def generate_default_simulation(self) -> Graph:
        """Genera una simulación por defecto (15 nodos, 20 aristas)."""
        return self.generate_connected_graph(n_nodes=15, m_edges=20)