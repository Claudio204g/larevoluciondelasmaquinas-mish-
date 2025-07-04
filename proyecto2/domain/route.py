from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class RouteAlgorithm(Enum):
    """Algoritmos disponibles para cálculo de rutas"""
    DIJKSTRA = "dijkstra"
    FLOYD_WARSHALL = "floyd_warshall"

@dataclass
class Route:
    """Clase que representa una ruta entre nodos"""
    path: List[str]  # Lista de IDs de nodos en orden de visita
    distance: float  # Distancia total
    energy_required: float  # Energía total requerida
    algorithm_used: RouteAlgorithm
    recharge_stops: List[str] = None  # IDs de nodos de recarga
    metadata: Optional[Dict] = None  # Datos adicionales

    def __post_init__(self):
        if self.recharge_stops is None:
            self.recharge_stops = []
        if self.metadata is None:
            self.metadata = {}

    def is_feasible(self, max_autonomy: float = 50.0) -> bool:
        """
        Verifica si la ruta es factible considerando la autonomía máxima del dron.
        Devuelve True si la ruta no excede la autonomía o si incluye recargas suficientes.
        """
        if self.energy_required <= max_autonomy:
            return True
        
        # Verificar que las recargas dividen la ruta en segmentos factibles
        if not self.recharge_stops:
            return False
        
        # Simular el viaje por segmentos
        current_energy = max_autonomy
        previous_node = self.path[0]
        
        for node in self.path[1:]:
            segment_cost = self.metadata.get(f"{previous_node}-{node}", {}).get("energy", 0)
            current_energy -= segment_cost
            
            if current_energy < 0:
                return False
            
            if node in self.recharge_stops:
                current_energy = max_autonomy  # Recarga completa
                
            previous_node = node
            
        return True

    def add_recharge_stop(self, node_id: str):
        """Añade una parada de recarga a la ruta"""
        if node_id not in self.path:
            raise ValueError("El nodo de recarga debe estar en la ruta")
        if node_id not in self.recharge_stops:
            self.recharge_stops.append(node_id)

    def to_string(self) -> str:
        """Representación de la ruta como string (para visualización)"""
        return " → ".join(self.path)