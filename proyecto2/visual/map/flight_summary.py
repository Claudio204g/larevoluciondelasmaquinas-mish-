from typing import List
from ...model import Graph

class FlightSummary:
    """Clase para calcular resúmenes de vuelo y consumo energético."""
    
    def __init__(self, graph: Graph, max_autonomy: float = 50.0):
        self.graph = graph
        self.max_autonomy = max_autonomy
    
    def calculate_route_energy(self, path: List[str]) -> float:
        """Calcula el consumo energético total de una ruta."""
        total_energy = 0.0
        
        for i in range(len(path) - 1):
            source_id = path[i]
            target_id = path[i+1]
            
            # Buscar la arista correspondiente
            edge_weight = None
            for edge in self.graph.edges:
                if edge.source_id == source_id and edge.target_id == target_id:
                    edge_weight = edge.weight
                    break
            
            if edge_weight is None:
                raise ValueError(f"No se encontró arista entre {source_id} y {target_id}")
            
            total_energy += edge_weight
        
        return total_energy
    
    def estimate_flight_time(self, path: List[str], avg_speed: float = 40.0) -> float:
        """
        Estima el tiempo de vuelo en minutos.
        avg_speed: velocidad promedio del dron en km/h
        """
        total_distance = self.calculate_route_energy(path)  # Asumimos que el peso es distancia en km
        return (total_distance / avg_speed) * 60  # Convertir a minutos
    
    def needs_recharge(self, path: List[str]) -> bool:
        """Determina si la ruta requiere paradas de recarga."""
        return self.calculate_route_energy(path) > self.max_autonomy
    
    def suggest_recharge_stops(self, path: List[str]) -> List[str]:
        """Sugiere nodos de recarga para una ruta que excede la autonomía."""
        if not self.needs_recharge(path):
            return []
        
        recharge_stops = []
        current_energy = 0.0
        
        for i in range(len(path) - 1):
            source_id = path[i]
            target_id = path[i+1]
            
            # Buscar el peso de la arista
            edge_weight = None
            for edge in self.graph.edges:
                if edge.source_id == source_id and edge.target_id == target_id:
                    edge_weight = edge.weight
                    break
            
            if edge_weight is None:
                raise ValueError(f"No se encontró arista entre {source_id} y {target_id}")
            
            # Verificar si necesitamos recargar antes de este segmento
            if current_energy + edge_weight > self.max_autonomy:
                # Encontrar el nodo de recarga más cercano a source_id
                nearest_recharge = self._find_nearest_recharge(source_id)
                if nearest_recharge:
                    recharge_stops.append(nearest_recharge)
                    current_energy = 0.0
            
            current_energy += edge_weight
        
        return recharge_stops
    
    def _find_nearest_recharge(self, node_id: str) -> str:
        """Encuentra el nodo de recarga más cercano al nodo dado."""
        recharge_nodes = [v.id for v in self.graph.vertices.values() 
                         if v.vertex_type.value == "recharge"]
        if not recharge_nodes:
            return None
        
        # Usar Dijkstra para encontrar el más cercano
        min_distance = float('inf')
        nearest_recharge = None
        
        for recharge_id in recharge_nodes:
            try:
                _, distance = self.graph.dijkstra(node_id, recharge_id)
                if distance < min_distance:
                    min_distance = distance
                    nearest_recharge = recharge_id
            except ValueError:
                continue
        
        return nearest_recharge
    
    def generate_flight_summary(self, path: List[str]) -> dict:
        """Genera un resumen completo del vuelo."""
        energy = self.calculate_route_energy(path)
        time_estimate = self.estimate_flight_time(path)
        needs_recharge = self.needs_recharge(path)
        recharge_stops = self.suggest_recharge_stops(path) if needs_recharge else []
        
        return {
            "total_energy": energy,
            "estimated_time": time_estimate,
            "needs_recharge": needs_recharge,
            "recharge_stops": recharge_stops,
            "is_feasible": energy <= self.max_autonomy or bool(recharge_stops)
        }