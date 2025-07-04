from dataclasses import dataclass
from typing import Optional

@dataclass
class Edge:
    """
    Representa una arista/conexión entre dos vértices en el grafo.
    """
    source_id: str
    target_id: str
    weight: float  # Distancia o costo de viaje
    is_active: bool = True
    drone_capacity: int = 1  # Número máximo de drones que pueden usarla simultáneamente
    id: Optional[str] = None  # Identificador opcional

    def __post_init__(self):
        if not self.id:
            self.id = f"{self.source_id}-{self.target_id}"

    def reverse(self) -> 'Edge':
        """Crea una nueva arista con dirección opuesta."""
        return Edge(
            source_id=self.target_id,
            target_id=self.source_id,
            weight=self.weight,
            is_active=self.is_active,
            drone_capacity=self.drone_capacity,
            id=f"{self.target_id}-{self.source_id}" if self.id else None
        )

    def to_dict(self) -> dict:
        """Convierte el objeto Edge a un diccionario para serialización."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "weight": self.weight,
            "is_active": self.is_active,
            "drone_capacity": self.drone_capacity
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Edge':
        """Crea un objeto Edge desde un diccionario."""
        return cls(
            id=data.get("id"),
            source_id=data["source_id"],
            target_id=data["target_id"],
            weight=data["weight"],
            is_active=data.get("is_active", True),
            drone_capacity=data.get("drone_capacity", 1)
        )

    def __str__(self):
        return f"{self.source_id} -> {self.target_id} (w: {self.weight})"