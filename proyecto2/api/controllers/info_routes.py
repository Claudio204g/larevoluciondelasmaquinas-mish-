from fastapi import APIRouter
from typing import List
from ..models import Client, Order

router = APIRouter()

@router.get("/reports/visits/clients")
def get_top_clients():
    """Obtener ranking de clientes más visitados"""
    # En un sistema real, esto vendría de la base de datos
    return [
        {"client_id": "C001", "name": "Cliente 1", "visits": 12},
        {"client_id": "C002", "name": "Cliente 2", "visits": 8}
    ]

@router.get("/reports/visits/recharges")
def get_top_recharge_nodes():
    """Obtener ranking de nodos de recarga más visitados"""
    return [
        {"node_id": "R001", "visits": 15},
        {"node_id": "R002", "visits": 10}
    ]

@router.get("/reports/visits/storages")
def get_top_storage_nodes():
    """Obtener ranking de nodos de almacenamiento más visitados"""
    return [
        {"node_id": "S001", "visits": 20},
        {"node_id": "S002", "visits": 18}
    ]

@router.get("/reports/summary")
def get_system_summary():
    """Obtener resumen general de la simulación"""
    return {
        "total_clients": 25,
        "total_orders": 120,
        "completed_orders": 85,
        "pending_orders": 15,
        "in_progress_orders": 20,
        "average_route_distance": 35.4,
        "average_energy_usage": 42.1,
        "most_used_recharge": "R001",
        "most_active_storage": "S001"
    }