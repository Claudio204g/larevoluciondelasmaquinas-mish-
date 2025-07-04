import folium
from ...model import Graph, Vertex

class MapBuilder:
    """Clase para construir mapas interactivos con Folium."""
    
    def __init__(self, center_coords=(-38.7397, -72.5984), zoom_start=13):
        """Inicializa el mapa centrado en Temuco por defecto."""
        self.center_coords = center_coords
        self.zoom_start = zoom_start
        self.map = folium.Map(location=center_coords, zoom_start=zoom_start)
    
    def add_vertex(self, vertex: Vertex):
        """Añade un vértice/nodo al mapa."""
        color = self._get_vertex_color(vertex.vertex_type)
        folium.Marker(
            location=vertex.coordinates,
            popup=f"{vertex.id} ({vertex.vertex_type.value})",
            icon=folium.Icon(color=color, icon="circle")
        ).add_to(self.map)
    
    def add_edge(self, source: Vertex, target: Vertex, color='gray', weight=1, opacity=0.7, dash_array=None):
        """Añade una arista/conexión al mapa."""
        folium.PolyLine(
            locations=[source.coordinates, target.coordinates],
            color=color,
            weight=weight,
            opacity=opacity,
            dash_array=dash_array
        ).add_to(self.map)
    
    def highlight_route(self, graph: Graph, path: list, base_map=None):
        """Resalta una ruta específica en el mapa."""
        if base_map:
            self.map = base_map
        else:
            self.map = folium.Map(location=self.center_coords, zoom_start=self.zoom_start)
        
        # Añadir todos los nodos
        for vertex in graph.vertices.values():
            self.add_vertex(vertex)
        
        # Resaltar ruta
        for i in range(len(path) - 1):
            source = graph.vertices[path[i]]
            target = graph.vertices[path[i+1]]
            self.add_edge(source, target, color='red', weight=3, opacity=1)
        
        return self.map
    
    def show_mst(self, graph: Graph, mst_edges: list):
        """Muestra el árbol de expansión mínima en el mapa."""
        self.map = folium.Map(location=self.center_coords, zoom_start=self.zoom_start)
        
        # Añadir nodos
        for vertex in graph.vertices.values():
            self.add_vertex(vertex)
        
        # Añadir aristas del MST
        for edge in mst_edges:
            source = graph.vertices[edge.source_id]
            target = graph.vertices[edge.target_id]
            self.add_edge(source, target, color='blue', weight=2, opacity=0.7, dash_array='5, 5')
        
        return self.map
    
    def _get_vertex_color(self, vertex_type):
        """Retorna el color correspondiente al tipo de vértice."""
        colors = {
            "storage": "blue",
            "recharge": "green",
            "client": "orange"
        }
        return colors.get(vertex_type.value, "gray")
    
    def get_map(self):
        """Retorna el mapa construido."""
        return self.map