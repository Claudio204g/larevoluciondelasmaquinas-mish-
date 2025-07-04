from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Route:
    """
    Representa una ruta entre nodos en el sistema de drones.
    """
    path: List[str]  # Lista de IDs de nodos en el camino
    total_cost: float  # Costo total de la ruta (suma de pesos)
    energy_required: float  # Energía requerida para completar la ruta
    recharge_stops: int = 0  # Número de paradas de recarga necesarias
    frequency: int = 1  # Cuántas veces se ha usado esta ruta

    def add_recharge_stop(self):
        """Incrementa el contador de paradas de recarga."""
        self.recharge_stops += 1

    def increment_frequency(self):
        """Incrementa la frecuencia de uso de esta ruta."""
        self.frequency += 1

    def is_valid(self, max_autonomy: float = 50.0) -> bool:
        """
        Verifica si la ruta es válida considerando la autonomía máxima del dron.
        """
        return self.energy_required <= max_autonomy

    def to_dict(self) -> dict:
        """Convierte el objeto Route a un diccionario para serialización."""
        return {
            "path": self.path,
            "total_cost": self.total_cost,
            "energy_required": self.energy_required,
            "recharge_stops": self.recharge_stops,
            "frequency": self.frequency
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Route':
        """Crea un objeto Route desde un diccionario."""
        return cls(
            path=data.get("path", []),
            total_cost=data.get("total_cost", 0.0),
            energy_required=data.get("energy_required", 0.0),
            recharge_stops=data.get("recharge_stops", 0),
            frequency=data.get("frequency", 1)
        )

    def __str__(self) -> str:
        """Representación de la ruta como string (para usar como clave en AVL)."""
        return "→".join(self.path)