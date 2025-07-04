class AVLNode:
    """Nodo para el árbol AVL que almacena rutas y sus frecuencias."""
    def __init__(self, key, value):
        self.key = key  # Ruta (string)
        self.value = value  # Frecuencia (int)
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    """Implementación de árbol AVL para registrar y consultar rutas frecuentes."""
    def __init__(self):
        self.root = None
    
    def insert(self, key, value):
        """Inserta una nueva ruta o actualiza su frecuencia si ya existe."""
        self.root = self._insert(self.root, key, value)
    
    def _insert(self, node, key, value):
        # Inserción estándar en BST
        if not node:
            return AVLNode(key, value)
        elif key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Ruta ya existe, incrementar frecuencia
            node.value += value
            return node
        
        # Actualizar altura del nodo
        node.height = 1 + max(self._get_height(node.left), 
                            self._get_height(node.right))
        
        # Balancear el árbol
        balance = self._get_balance(node)
        
        # Casos de desbalance
        # Left Left
        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)
        
        # Right Right
        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)
        
        # Left Right
        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        
        # Right Left
        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        
        return node
    
    def search(self, key):
        """Busca una ruta y retorna su frecuencia, o None si no existe."""
        return self._search(self.root, key)
    
    def _search(self, node, key):
        if not node:
            return None
        elif key == node.key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)
    
    def get_most_frequent(self, n=5):
        """Retorna las n rutas más frecuentes."""
        routes = []
        self._inorder_traversal(self.root, routes)
        routes.sort(key=lambda x: x.value, reverse=True)
        return routes[:n]
    
    def _inorder_traversal(self, node, result):
        """Recorrido inorder para obtener todas las rutas."""
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node)
            self._inorder_traversal(node.right, result)
    
    def _get_height(self, node):
        if not node:
            return 0
        return node.height
    
    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        # Rotación
        y.left = z
        z.right = T2
        
        # Actualizar alturas
        z.height = 1 + max(self._get_height(z.left), 
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), 
                           self._get_height(y.right))
        
        return y
    
    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        # Rotación
        y.right = z
        z.left = T3
        
        # Actualizar alturas
        z.height = 1 + max(self._get_height(z.left), 
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), 
                           self._get_height(y.right))
        
        return y
    
    def to_dict(self):
        """Serializa el árbol a un diccionario."""
        result = []
        self._serialize(self.root, result)
        return {"avl_tree": result}
    
    def _serialize(self, node, result):
        if node:
            result.append({"key": node.key, "value": node.value})
            self._serialize(node.left, result)
            self._serialize(node.right, result)
    
    @classmethod
    def from_dict(cls, data):
        """Reconstruye el árbol desde un diccionario serializado."""
        avl = cls()
        for item in data.get("avl_tree", []):
            avl.insert(item["key"], item["value"])
        return avl