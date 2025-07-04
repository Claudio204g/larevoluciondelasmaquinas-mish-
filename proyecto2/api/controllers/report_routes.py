from fastapi import APIRouter
from fastapi.responses import FileResponse
import tempfile
from visual.map.report_generator import ReportGenerator 

router = APIRouter()

def get_simulation():
    """Función helper para obtener la instancia de simulación."""
    from api.main import get_simulation  # Importación absoluta
    return get_simulation()

@router.get("/reports/pdf")
async def generate_pdf_report():
    """Genera y descarga un informe PDF con estadísticas del sistema."""
    sim = get_simulation()
    report_gen = ReportGenerator(sim)
    pdf_path = report_gen.generate_route_report()
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="informe_drones.pdf"
    )