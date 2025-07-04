import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from model.graph import Graph
from domain.client import Client
from domain.order import Order, OrderStatus
from domain.route import Route
from tda.avl import AVLTree

class Simulation:
    """
    Clase principal que controla la simulación del sistema logístico con drones.
    """
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.clients: Dict[str, Client] = {}
        self.orders: Dict[str, Order] = {}
        self.routes: Dict[str, Route] = {}
        self.avl_routes = AVLTree()  # Se inicializará con un AVL después
        self.current_time = datetime.now()
        self.drone_autonomy = 50.0  # Autonomía máxima del dron en unidades de costo
        self.simulation_speed = 10  # Velocidad de simulación (1x = tiempo real)
        self.storage_visits = {}
        self.recharge_visits = {}
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa los clientes a partir de los nodos de tipo CLIENTE en el grafo."""
        client_nodes = [v for v in self.graph.vertices.values() if v.vertex_type.value == "client"]
        
        for i, vertex in enumerate(client_nodes):
            client_id = f"client_{i}"
            self.clients[client_id] = Client(
                id=client_id,
                name=f"Cliente {vertex.name.split()[-1]}",
                client_type=random.choice(["regular", "priority", "vip"]),
                coordinates=vertex.coordinates,
                contact_phone=f"+569{random.randint(10000000, 99999999)}"
                
            )
            vertex.client_id = client_id
    
    def generate_random_order(self) -> Order:
        """Genera una orden aleatoria entre un nodo de almacenamiento y un cliente."""
        storage_nodes = [v.id for v in self.graph.vertices.values() 
                        if v.vertex_type.value == "storage"]
        client_vertices = [v for v in self.graph.vertices.values() 
                          if v.vertex_type.value == "client"]
        
        if not storage_nodes or not client_vertices:
            raise ValueError("No hay nodos de almacenamiento o clientes en el grafo")
        
        origin_id = random.choice(storage_nodes)
        client_vertex = random.choice(client_vertices)
        client_id = client_vertex.client_id 
        
        order = Order(
            id=f"order_{len(self.orders) + 1}",
            client_id=client_id,
            origin_id=origin_id,
            destination_id=client_vertex.id,
            priority=random.randint(1, 5),
            created_at=self.current_time
        )
        
        self.orders[order.id] = order
        self.clients[client_id].increment_orders()
        
        return order
    
    def calculate_route(self, origin_id: str, destination_id: str, 
                       algorithm: str = "dijkstra") -> Route:
        """
        Calcula la ruta entre dos nodos considerando la autonomía del dron.
        Si la ruta directa excede la autonomía, incluye paradas de recarga.
        """
        if algorithm == "dijkstra":
            path, total_cost = self.graph.dijkstra(origin_id, destination_id)
        elif algorithm == "floyd-warshall":
            fw_matrix = self.graph.floyd_warshall()
            total_cost = fw_matrix[origin_id][destination_id]
            # Reconstruir el camino sería necesario aquí (implementación omitida por brevedad)
            path = []  # Placeholder - implementar reconstrucción de camino
    
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        
        if not path:
            raise ValueError("No se encontró camino entre los nodos")
        
        for node_id in path:
            v = self.graph.vertices[node_id]
            if v.vertex_type.value == "recharge":
                self.recharge_visits[node_id] = self.recharge_visits.get(node_id, 0) + 1
            elif v.vertex_type.value == "storage":
                self.storage_visits[node_id] = self.storage_visits.get(node_id, 0) + 1
                
        # Verificar si necesita recargas
        route_obj = Route(
            path=path,
            total_cost=total_cost,
            energy_required=total_cost,
            recharge_stops=0
        )
        
        if total_cost > self.drone_autonomy:
            route_obj = self._add_recharge_stops(route_obj)
        
        # Registrar la ruta
        route_id = f"route_{len(self.routes) + 1}"
        self.routes[route_id] = route_obj
        
        # Actualizar AVL de rutas frecuentes
        if self.avl_routes:
            route_key = "→".join(route_obj.path)
            existing = self.avl_routes.search(route_key)
            if existing:
                existing.value += 1
            else:
                self.avl_routes.insert(route_key, 1)
        
        return route_obj
    
    def _add_recharge_stops(self, original_route: Route) -> Route:
        """
        Modifica una ruta para incluir paradas de recarga cuando se excede la autonomía.
        """
        new_path = []
        current_energy = 0.0
        recharge_stops = 0
        
        for i in range(len(original_route.path) - 1):
            from_node = original_route.path[i]
            to_node = original_route.path[i+1]
            
            # Encontrar el peso de esta arista
            edge_weight = None
            for edge in self.graph.edges:
                if edge.source_id == from_node and edge.target_id == to_node:
                    edge_weight = edge.weight
                    break
            
            if edge_weight is None:
                raise ValueError(f"No se encontró arista entre {from_node} y {to_node}")
            
            # Verificar si necesitamos recargar antes de este segmento
            if current_energy + edge_weight > self.drone_autonomy:
                # Encontrar el nodo de recarga más cercano a from_node
                nearest_recharge = self._find_nearest_recharge(from_node)
                if nearest_recharge:
                    new_path.append(nearest_recharge)
                    recharge_stops += 1
                    current_energy = 0.0
            
            new_path.append(from_node)
            current_energy += edge_weight
        
        # Añadir el último nodo
        new_path.append(original_route.path[-1])
        
        # Recalcular costo total (puede ser diferente por las paradas extra)
        total_cost = 0.0
        for i in range(len(new_path) - 1):
            for edge in self.graph.edges:
                if edge.source_id == new_path[i] and edge.target_id == new_path[i+1]:
                    total_cost += edge.weight
                    break
        
        return Route(
            path=new_path,
            total_cost=total_cost,
            energy_required=total_cost,
            recharge_stops=recharge_stops
        )
    
    def _find_nearest_recharge(self, node_id: str) -> Optional[str]:
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
    
    def complete_order(self, order_id: str, route: Route) -> Order:
        """Marca una orden como completada y registra la ruta utilizada."""
        if order_id not in self.orders:
            raise ValueError(f"Orden {order_id} no existe")
        
        order = self.orders[order_id]
        order.route = route.path
        order.energy_cost = route.total_cost
        order.complete()
        
        return order
    
    def update_simulation(self, delta_time: timedelta):
        """Actualiza el estado de la simulación avanzando el tiempo."""
        self.current_time += delta_time * self.simulation_speed
        
        # Aquí se podrían añadir actualizaciones de estado de órdenes, etc.
        # Por ejemplo, órdenes que pasan a "entregadas" automáticamente después de un tiempo
    
    def get_simulation_stats(self) -> dict:
        """Retorna estadísticas clave de la simulación."""
        return {
            "total_nodes": len(self.graph.vertices),
            "total_edges": len(self.graph.edges),
            "total_clients": len(self.clients),
            "total_orders": len(self.orders),
            "completed_orders": sum(1 for o in self.orders.values() 
                                  if o.status == OrderStatus.DELIVERED),
            "pending_orders": sum(1 for o in self.orders.values() 
                                 if o.status == OrderStatus.PENDING),
            "timestamp": self.current_time.isoformat()
        }
    
    def to_dict(self) -> dict:
        """Serializa el estado de la simulación a un diccionario."""
        return {
            "graph": self.graph.to_dict(),
            "clients": {k: v.to_dict() for k, v in self.clients.items()},
            "orders": {k: v.to_dict() for k, v in self.orders.items()},
            "routes": {k: v.to_dict() for k, v in self.routes.items()},
            "current_time": self.current_time.isoformat(),
            "drone_autonomy": self.drone_autonomy
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea una simulación desde un diccionario serializado."""
        from model import Graph
        graph = Graph.from_dict(data["graph"])
        sim = cls(graph)
        
        sim.clients = {k: Client.from_dict(v) for k, v in data["clients"].items()}
        sim.orders = {k: Order.from_dict(v) for k, v in data["orders"].items()}
        sim.routes = {k: Route.from_dict(v) for k, v in data["routes"].items()}
        sim.current_time = datetime.fromisoformat(data["current_time"])
        sim.drone_autonomy = data.get("drone_autonomy", 50.0)
        
        return sim