from fastapi import APIRouter, HTTPException
from domain.order import Order, OrderStatus
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/orders/", response_model=List[Order])
async def get_all_orders():
    """Obtiene todas las órdenes del sistema."""
    sim = get_simulation()
    return list(sim.orders.values())

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Obtiene una orden específica por su ID."""
    sim = get_simulation()
    order = sim.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order

@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancela una orden específica."""
    sim = get_simulation()
    order = sim.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Solo se pueden cancelar órdenes pendientes"
        )
    
    order.cancel()
    return {"message": f"Orden {order_id} cancelada exitosamente"}

@router.post("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Marca una orden como completada."""
    sim = get_simulation()
    order = sim.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.IN_TRANSIT]:
        raise HTTPException(
            status_code=400, 
            detail="La orden no está en estado cancelable"
        )
    
    order.complete()
    return {"message": f"Orden {order_id} marcada como completada"}

def get_simulation():
    """Función helper para obtener la instancia de simulación."""
    from api.main import get_simulation
    return get_simulation()