from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

class VertexType(Enum):
    STORAGE = "storage"
    RECHARGE = "recharge"
    CLIENT = "client"

@dataclass
class Vertex:
    """
    Representa un vértice/nodo en el grafo del sistema de drones.
    """
    id: str
    vertex_type: VertexType
    coordinates: Tuple[float, float]  # (latitud, longitud)
    name: Optional[str] = None
    energy_available: float = 0.0  # Solo relevante para nodos de recarga

    def __hash__(self):
        return hash(self.id)

    def to_dict(self) -> dict:
        """Convierte el objeto Vertex a un diccionario para serialización."""
        return {
            "id": self.id,
            "type": self.vertex_type.value,
            "coordinates": self.coordinates,
            "name": self.name,
            "energy_available": self.energy_available
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Vertex':
        """Crea un objeto Vertex desde un diccionario."""
        return cls(
            id=data["id"],
            vertex_type=VertexType(data["type"]),
            coordinates=tuple(data["coordinates"]),
            name=data.get("name"),
            energy_available=data.get("energy_available", 0.0)
        )

    def __str__(self):
        return f"{self.id} ({self.vertex_type.value})"