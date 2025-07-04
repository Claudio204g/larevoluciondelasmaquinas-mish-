import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from ..model import Graph

class NetworkXAdapter:
    """Adaptador para visualizar grafos usando NetworkX y Matplotlib."""
    
    def __init__(self):
        self.graph = None
    
    def create_from_graph(self, graph: Graph):
        """Crea un grafo NetworkX a partir de nuestro modelo Graph."""
        self.graph = nx.Graph()
        
        # Añadir nodos
        for vertex in graph.vertices.values():
            self.graph.add_node(
                vertex.id,
                type=vertex.vertex_type.value,
                pos=vertex.coordinates
            )
        
        # Añadir aristas
        for edge in graph.edges:
            self.graph.add_edge(
                edge.source_id,
                edge.target_id,
                weight=edge.weight
            )
        
        return self.graph
    
    def draw_graph(self, with_labels=True, node_size=500, figsize=(10, 8)):
        """Dibuja el grafo usando Matplotlib."""
        if not self.graph:
            raise ValueError("Primero debe crear un grafo con create_from_graph()")
        
        plt.figure(figsize=figsize)
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Asignar colores según el tipo de nodo
        node_colors = []
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node]['type']
            if node_type == "storage":
                node_colors.append("blue")
            elif node_type == "recharge":
                node_colors.append("green")
            else:
                node_colors.append("orange")
        
        nx.draw(
            self.graph,
            pos,
            with_labels=with_labels,
            node_size=node_size,
            node_color=node_colors,
            font_size=8,
            font_weight="bold"
        )
        
        # Guardar la figura en un buffer
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer
    
    def draw_mst(self, mst_edges, figsize=(10, 8)):
        """Dibuja el árbol de expansión mínima."""
        if not self.graph:
            raise ValueError("Primero debe crear un grafo con create_from_graph()")
        
        mst = nx.Graph()
        
        # Añadir solo las aristas del MST
        for edge in mst_edges:
            mst.add_edge(
                edge.source_id,
                edge.target_id,
                weight=edge.weight
            )
        
        plt.figure(figsize=figsize)
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Dibujar el grafo completo en gris claro de fondo
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_size=300,
            node_color="lightgray"
        )
        
        # Dibujar el MST en azul
        nx.draw_networkx_edges(
            mst,
            pos,
            edge_color="blue",
            width=2,
            style="dashed"
        )
        
        # Dibujar etiquetas
        nx.draw_networkx_labels(
            self.graph,
            pos,
            font_size=8,
            font_weight="bold"
        )
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer