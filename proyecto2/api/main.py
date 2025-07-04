from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers import client_routes, order_routes, report_routes, info_routes

app = FastAPI(
    title="API Sistema Logístico con Drones",
    description="API para el sistema de drones autónomos de Correos Chile",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(client_routes.router, prefix="/clients", tags=["Clients"])
app.include_router(order_routes.router, prefix="/orders", tags=["Orders"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(info_routes.router, prefix="/info", tags=["Info"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API del Sistema Logístico con Drones"}