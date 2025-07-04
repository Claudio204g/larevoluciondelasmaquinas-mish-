from fastapi import APIRouter, HTTPException
from domain.client import Client
from typing import List
import json

router = APIRouter()

@router.get("/clients/", response_model=List[Client])
async def get_all_clients():
    """Obtiene todos los clientes registrados en el sistema."""
    sim = get_simulation()
    return list(sim.clients.values())

@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    """Obtiene un cliente específico por su ID."""
    sim = get_simulation()
    client = sim.clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

def get_simulation():
    """Función helper para obtener la instancia de simulación."""
    from api.main import get_simulation
    return get_simulation()