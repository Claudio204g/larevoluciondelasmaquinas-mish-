import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from tda import AVLTree, AVLNode

class AVLVisualizer:
    """Clase para visualizar árboles AVL usando NetworkX."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def create_from_avl(self, avl_tree: AVLTree):
        """Crea un grafo NetworkX a partir de un árbol AVL."""
        self.graph = nx.DiGraph()
        self._add_nodes_recursive(avl_tree.root)
        return self.graph
    
    def _add_nodes_recursive(self, node: AVLNode, parent=None):
        """Función recursiva para añadir nodos al grafo."""
        if node:
            # Añadir nodo actual
            self.graph.add_node(
                node.key,
                label=f"{node.key[:15]}...\nFreq: {node.value}" if len(node.key) > 15 
                      else f"{node.key}\nFreq: {node.value}"
            )
            
            # Conectar con el padre si existe
            if parent:
                self.graph.add_edge(parent.key, node.key)
            
            # Procesar hijos recursivamente
            self._add_nodes_recursive(node.left, node)
            self._add_nodes_recursive(node.right, node)
    
    def draw_avl(self, figsize=(12, 8), node_size=3000):
        """Dibuja el árbol AVL usando Matplotlib."""
        if len(self.graph.nodes) == 0:
            raise ValueError("Primero debe crear un grafo con create_from_avl()")
        
        plt.figure(figsize=figsize)
        pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot")
        
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            labels=nx.get_node_attributes(self.graph, 'label'),
            node_size=node_size,
            node_color="skyblue",
            font_size=8,
            font_weight="bold",
            arrows=True
        )
        
        plt.title("Árbol AVL de Rutas Frecuentes")
        
        # Guardar la figura en un buffer
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer