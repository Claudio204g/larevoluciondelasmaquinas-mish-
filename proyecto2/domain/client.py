from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    """
    Representa un cliente que recibe entregas de drones.
    """
    id: str
    name: str
    client_type: str  # "regular", "priority", etc.
    coordinates: tuple[float, float]  # (lat, lng)
    total_orders: int = 0
    contact_phone: Optional[str] = None

    def increment_orders(self):
        """Incrementa el contador de pedidos del cliente."""
        self.total_orders += 1

    def to_dict(self) -> dict:
        """Convierte el objeto Client a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.client_type,
            "coordinates": self.coordinates,
            "total_orders": self.total_orders,
            "contact_phone": self.contact_phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Crea un objeto Client desde un diccionario."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            client_type=data.get("type"),
            coordinates=data.get("coordinates"),
            total_orders=data.get("total_orders", 0),
            contact_phone=data.get("contact_phone")
        )