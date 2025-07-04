from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime
from uuid import uuid4
from typing import Optional
from typing import List
class OrderStatus(Enum):
    """Estados posibles de una orden"""
    PENDING = auto()
    IN_PROGRESS = auto()
    IN_TRANSIT = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    NEEDS_RECHARGE = auto()

@dataclass
class Order:
    """Clase que representa una orden de entrega"""
    id: str
    client_id: str
    origin: str  # ID del nodo de almacenamiento
    destination: str  # ID del nodo cliente
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = datetime.now()
    priority: int = 1  # 1-5, siendo 5 la mayor prioridad
    delivery_date: Optional[datetime] = None
    total_cost: float = 0.0
    route: Optional[List[str]] = None  # Lista de nodos en la ruta
    energy_required: float = 0.0
    recharge_stops: List[str] = None  # IDs de nodos de recarga usados

    def __post_init__(self):
        if self.recharge_stops is None:
            self.recharge_stops = []

    def update_status(self, new_status: OrderStatus):
        """Actualiza el estado de la orden con validaciones"""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.IN_TRANSIT, OrderStatus.CANCELLED],
            OrderStatus.IN_TRANSIT: [OrderStatus.COMPLETED, OrderStatus.NEEDS_RECHARGE],
            OrderStatus.NEEDS_RECHARGE: [OrderStatus.IN_TRANSIT, OrderStatus.CANCELLED]
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Transición inválida de {self.status} a {new_status}")
        
        self.status = new_status
        
        if new_status == OrderStatus.COMPLETED:
            self.delivery_date = datetime.now()

    def calculate_cost(self, distance: float, energy_cost: float):
        """Calcula el costo total basado en distancia y energía"""
        # Fórmula de ejemplo: costo base + (distancia * factor) + (energía * costo_energía)
        base_cost = 10.0
        distance_factor = 0.5
        energy_rate = 0.3
        
        self.total_cost = base_cost + (distance * distance_factor) + (self.energy_required * energy_rate)
        return self.total_cost

    @classmethod
    def create_new(cls, client_id: str, origin: str, destination: str, priority: int = 1):
        """Factory method para crear nuevas órdenes"""
        return cls(
            id=str(uuid4()),
            client_id=client_id,
            origin=origin,
            destination=destination,
            priority=priority
        )