class HashMap:
    """Implementación de un HashMap para búsqueda rápida de clientes y pedidos."""
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]
    
    def _hash(self, key):
        """Función de hash para convertir una clave en un índice."""
        return hash(key) % self.capacity
    
    def put(self, key, value):
        """Inserta o actualiza un valor en el mapa."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        # Buscar si la clave ya existe
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Si no existe, añadirla
        bucket.append((key, value))
        self.size += 1
        
        # Rehash si el factor de carga es muy alto
        if self.size / self.capacity > 0.7:
            self._rehash()
    
    def get(self, key):
        """Obtiene un valor por su clave, o None si no existe."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        return None
    
    def remove(self, key):
        """Elimina una clave del mapa."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        
        return False
    
    def _rehash(self):
        """Redimensiona el mapa cuando se llena."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)
    
    def __contains__(self, key):
        return self.get(key) is not None
    
    def __len__(self):
        return self.size
    
    def keys(self):
        """Retorna todas las claves en el mapa."""
        keys = []
        for bucket in self.buckets:
            for key, _ in bucket:
                keys.append(key)
        return keys
    
    def values(self):
        """Retorna todos los valores en el mapa."""
        values = []
        for bucket in self.buckets:
            for _, value in bucket:
                values.append(value)
        return values
    
    def items(self):
        """Retorna todos los pares clave-valor en el mapa."""
        items = []
        for bucket in self.buckets:
            items.extend(bucket)
        return items
    
    def to_dict(self):
        """Serializa el HashMap a un diccionario."""
        return {
            "capacity": self.capacity,
            "size": self.size,
            "entries": self.items()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Reconstruye el HashMap desde un diccionario serializado."""
        hash_map = cls(data["capacity"])
        for key, value in data["entries"]:
            hash_map.put(key, value)
        return hash_map