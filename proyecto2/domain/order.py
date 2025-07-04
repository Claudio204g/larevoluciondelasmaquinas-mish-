from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class Order:
    """
    Representa una orden de entrega a ser realizada por un dron.
    """
    id: str
    client_id: str
    origin_id: str  # ID del nodo de almacenamiento
    destination_id: str  # ID del nodo cliente
    created_at: datetime = datetime.now()
    status: OrderStatus = OrderStatus.PENDING
    priority: int = 1  # 1-5, siendo 5 la mayor prioridad
    route: Optional[List[str]] = None  # Lista de nodos en la ruta
    energy_cost: Optional[float] = None  # Costo energético estimado
    completed_at: Optional[datetime] = None

    def complete(self):
        """Marca la orden como completada."""
        self.status = OrderStatus.DELIVERED
        self.completed_at = datetime.now()

    def cancel(self):
        """Cancela la orden si está pendiente."""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELLED

    def to_dict(self) -> dict:
        """Convierte el objeto Order a un diccionario para serialización."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "origin_id": self.origin_id,
            "destination_id": self.destination_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "priority": self.priority,
            "route": self.route,
            "energy_cost": self.energy_cost,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Crea un objeto Order desde un diccionario."""
        return cls(
            id=data.get("id"),
            client_id=data.get("client_id"),
            origin_id=data.get("origin_id"),
            destination_id=data.get("destination_id"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now(),
            status=OrderStatus(data.get("status", "pending")),
            priority=data.get("priority", 1),
            route=data.get("route"),
            energy_cost=data.get("energy_cost"),
            completed_at=datetime.fromisoformat(data.get("completed_at")) if data.get("completed_at") else None
        )