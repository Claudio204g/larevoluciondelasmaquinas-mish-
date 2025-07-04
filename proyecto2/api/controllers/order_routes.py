from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Order, OrderStatus
from domain.order import Order as OrderDomain

router = APIRouter()

# Simulación de base de datos
orders_db = {}

@router.get("/", response_model=List[Order])
def get_all_orders():
    """Listar todas las órdenes registradas"""
    return list(orders_db.values())

@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Obtener detalle de una orden específica"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orders_db[order_id]

@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    """Cancelar una orden específica"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    order = orders_db[order_id]
    if order.status not in [OrderStatus.PENDING, OrderStatus.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="La orden no puede ser cancelada en su estado actual")
    
    order.status = OrderStatus.CANCELLED
    return {"message": f"Orden {order_id} cancelada exitosamente"}

@router.post("/orders/{order_id}/complete")
def complete_order(order_id: str):
    """Marcar una orden como completada"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    order = orders_db[order_id]
    if order.status != OrderStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="La orden no puede ser completada en su estado actual")
    
    order.status = OrderStatus.COMPLETED
    order.delivery_date = datetime.now()
    return {"message": f"Orden {order_id} completada exitosamente"}