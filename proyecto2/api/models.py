from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Client(BaseModel):
    id: str
    name: str
    type: str
    total_orders: int = 0

class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(BaseModel):
    id: str
    client_id: str
    origin: str
    destination: str
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = datetime.now()
    priority: int = 1
    delivery_date: Optional[datetime] = None
    total_cost: float = 0.0

class Route(BaseModel):
    id: str
    path: List[str]
    distance: float
    energy_usage: float
    recharge_stops: List[str] = []

class ReportData(BaseModel):
    frequent_routes: List[dict]
    top_clients: List[dict]
    top_nodes: List[dict]
    storage_usage: dict
    recharge_usage: dict