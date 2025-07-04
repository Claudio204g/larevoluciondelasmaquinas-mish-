from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Client
from domain.client import Client as ClientDomain

router = APIRouter()

# Simulación de base de datos
clients_db = {}

@router.get("/", response_model=List[Client])
def get_all_clients():
    """Obtener lista completa de clientes"""
    return list(clients_db.values())

@router.get("/{client_id}", response_model=Client)
def get_client(client_id: str):
    """Obtener información de un cliente específico"""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return clients_db[client_id]