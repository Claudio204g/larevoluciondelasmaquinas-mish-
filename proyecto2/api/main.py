from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers import client_routes, order_routes, report_routes, info_routes
from sim import Simulation
import uvicorn
import webbrowser
import threading

app = FastAPI(
    title="API del Sistema de Drones",
    description="API RESTful para el sistema logístico autónomo con drones",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(client_routes.router, prefix="/api/v1")
app.include_router(order_routes.router, prefix="/api/v1")
app.include_router(report_routes.router, prefix="/api/v1")
app.include_router(info_routes.router, prefix="/api/v1")

# Variable global para la simulación
simulation_instance = None

def get_simulation() -> Simulation:
    """Obtiene la instancia actual de la simulación."""
    global simulation_instance
    if simulation_instance is None:
        from sim import SimulationInitializer
        initializer = SimulationInitializer()
        graph = initializer.generate_connected_graph(15, 20)  # Valores por defecto
        simulation_instance = Simulation(graph)
    return simulation_instance

@app.get("/")
def root():
    return {"message": "API del Sistema de Drones"}

def open_docs():
    webbrowser.open_new("http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    threading.Timer(1.5, open_docs).start()  # Espera 1.5 segundos antes de abrir
    uvicorn.run(app, host="0.0.0.0", port=8000)