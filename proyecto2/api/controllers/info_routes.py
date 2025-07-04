from fastapi import APIRouter
from typing import List, Dict
from sim import Simulation

router = APIRouter()

@router.get("/info/visits/clients")
async def get_client_visits() -> List[Dict]:
    """Obtiene el ranking de clientes más visitados."""
    sim = get_simulation()
    clients = sorted(
        sim.clients.values(),
        key=lambda c: c.total_orders,
        reverse=True
    )
    return [
        {
            "client_id": client.id,
            "name": client.name,
            "total_orders": client.total_orders,
            "client_type": client.client_type
        }
        for client in clients
    ]

@router.get("/info/visits/recharges")
async def get_recharge_visits() -> List[Dict]:
    """Obtiene el ranking de nodos de recarga más visitados."""
    sim = get_simulation()
    # Implementar lógica para contar visitas a nodos de recarga
    # (Esto requeriría modificar la clase Simulation para llevar registro)
    return []

@router.get("/info/visits/storages")
async def get_storage_visits() -> List[Dict]:
    """Obtiene el ranking de nodos de almacenamiento más visitados."""
    sim = get_simulation()
    # Implementar lógica similar a get_recharge_visits()
    return []

@router.get("/info/summary")
async def get_system_summary() -> Dict:
    """Obtiene un resumen general del sistema."""
    sim = get_simulation()
    stats = sim.get_simulation_stats()
    return {
        "system_status": "active",
        "timestamp": stats["timestamp"],
        "total_nodes": stats["total_nodes"],
        "total_edges": stats["total_edges"],
        "total_clients": stats["total_clients"],
        "total_orders": stats["total_orders"],
        "completed_orders": stats["completed_orders"],
        "pending_orders": stats["pending_orders"]
    }

def get_simulation():
    """Función helper para obtener la instancia de simulación."""
    from api.main import get_simulation
    return get_simulation()