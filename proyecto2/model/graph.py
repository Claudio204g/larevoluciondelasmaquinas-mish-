from typing import Dict, List, Optional, Tuple
from heapq import heappop, heappush
from model.vertex import Vertex, VertexType
from model.edge import Edge

class Graph:
    """
    Representa el grafo completo del sistema de drones con métodos para:
    - Búsqueda de caminos (Dijkstra, Floyd-Warshall)
    - Árbol de expansión mínima (Kruskal)
    - Gestión de vértices y aristas
    """
    
    def __init__(self):
        self.vertices: Dict[str, Vertex] = {}
        self.edges: List[Edge] = []
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = {}
        self.floyd_warshall_cached = None

    def add_vertex(self, vertex: Vertex):
        """Añade un vértice al grafo."""
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex
            self.adjacency_list[vertex.id] = []
            self.floyd_warshall_cached = None  # Invalida cache

    def add_edge(self, edge: Edge, bidirectional: bool = True):
        """Añade una arista al grafo."""
        # Verifica que existan los vértices
        if edge.source_id not in self.vertices or edge.target_id not in self.vertices:
            raise ValueError("Los vértices de la arista deben existir en el grafo")
        
        self.edges.append(edge)
        self.adjacency_list[edge.source_id].append((edge.target_id, edge.weight))
        
        if bidirectional:
            reversed_edge = edge.reverse()
            self.edges.append(reversed_edge)
            self.adjacency_list[edge.target_id].append((edge.source_id, edge.weight))
        
        self.floyd_warshall_cached = None  # Invalida cache

    def dijkstra(self, start_id: str, end_id: str) -> Tuple[List[str], float]:
        """
        Implementa el algoritmo de Dijkstra para encontrar el camino más corto
        entre dos nodos. Retorna (camino, costo_total).
        """
        if start_id not in self.vertices or end_id not in self.vertices:
            raise ValueError("Vértices de inicio/fin no existen en el grafo")
        
        # Inicialización
        distances = {vertex: float('inf') for vertex in self.vertices}
        previous = {vertex: None for vertex in self.vertices}
        distances[start_id] = 0
        priority_queue = [(0, start_id)]
        
        while priority_queue:
            current_distance, current_vertex = heappop(priority_queue)
            
            if current_vertex == end_id:
                break
                
            if current_distance > distances[current_vertex]:
                continue
                
            for neighbor, weight in self.adjacency_list[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heappush(priority_queue, (distance, neighbor))
        
        # Reconstrucción del camino
        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end_id] if path else (None, float('inf'))

    def kruskal_mst(self) -> List[Edge]:
        """
        Implementa el algoritmo de Kruskal para encontrar el árbol de expansión mínima.
        Retorna una lista de aristas que forman el MST.
        """
        parent = {v_id: v_id for v_id in self.vertices}
        rank = {v_id: 0 for v_id in self.vertices}
        
        def find(v_id):
            if parent[v_id] != v_id:
                parent[v_id] = find(parent[v_id])
            return parent[v_id]
        
        def union(v1_id, v2_id):
            root1 = find(v1_id)
            root2 = find(v2_id)
            
            if root1 != root2:
                if rank[root1] > rank[root2]:
                    parent[root2] = root1
                else:
                    parent[root1] = root2
                    if rank[root1] == rank[root2]:
                        rank[root2] += 1
        
        # Ordenar aristas por peso
        sorted_edges = sorted(self.edges, key=lambda e: e.weight)
        mst = []
        
        for edge in sorted_edges:
            if find(edge.source_id) != find(edge.target_id):
                union(edge.source_id, edge.target_id)
                mst.append(edge)
                if len(mst) == len(self.vertices) - 1:
                    break
        
        return mst

    def floyd_warshall(self) -> Dict[str, Dict[str, float]]:
        """
        Implementa el algoritmo de Floyd-Warshall para encontrar todos los caminos mínimos.
        Retorna una matriz de distancias.
        """
        if self.floyd_warshall_cached:
            return self.floyd_warshall_cached
            
        dist = {v1: {v2: 0 if v1 == v2 else float('inf') for v2 in self.vertices} 
               for v1 in self.vertices}
        
        # Inicializar con distancias directas
        for edge in self.edges:
            if edge.weight < dist[edge.source_id][edge.target_id]:
                dist[edge.source_id][edge.target_id] = edge.weight
        
        # Calcular caminos mínimos
        for k in self.vertices:
            for i in self.vertices:
                for j in self.vertices:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        
        self.floyd_warshall_cached = dist
        return dist

    def get_vertex_by_type(self, vertex_type: str) -> List[Vertex]:
        """Filtra vértices por tipo."""
        return [v for v in self.vertices.values() if v.vertex_type.value == vertex_type]

    def to_dict(self) -> dict:
        """Convierte el grafo a un diccionario para serialización."""
        return {
            "vertices": {k: v.to_dict() for k, v in self.vertices.items()},
            "edges": [e.to_dict() for e in self.edges]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Graph':
        """Crea un grafo desde un diccionario."""
        graph = cls()
        for v_data in data["vertices"].values():
            graph.add_vertex(Vertex.from_dict(v_data))
        
        for e_data in data["edges"]:
            graph.add_edge(Edge.from_dict(e_data), bidirectional=False)
        
        return graph

    def __str__(self):
        return f"Graph(V={len(self.vertices)}, E={len(self.edges)})"