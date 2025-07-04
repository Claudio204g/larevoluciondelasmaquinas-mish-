from dataclasses import dataclass
from typing import List
from uuid import uuid4

@dataclass
class Client:
    """Clase que representa un cliente en el sistema logístico"""
    id: str
    name: str
    location: str  # Coordenadas o dirección
    client_type: str  # "regular", "priority", etc.
    total_orders: int = 0
    current_orders: List[str] = None  # IDs de órdenes activas

    def __post_init__(self):
        if self.current_orders is None:
            self.current_orders = []

    def add_order(self, order_id: str):
        """Registra una nueva orden para este cliente"""
        self.current_orders.append(order_id)
        self.total_orders += 1

    def complete_order(self, order_id: str):
        """Marca una orden como completada"""
        if order_id in self.current_orders:
            self.current_orders.remove(order_id)

    @classmethod
    def create_new(cls, name: str, location: str, client_type: str):
        """Factory method para crear nuevos clientes"""
        return cls(
            id=str(uuid4()),
            name=name,
            location=location,
            client_type=client_type
        )