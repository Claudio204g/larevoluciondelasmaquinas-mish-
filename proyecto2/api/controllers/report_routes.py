from fastapi import APIRouter
from fastapi.responses import FileResponse
from ..models import ReportData
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

router = APIRouter()

@router.get("/pdf", response_class=FileResponse)
def generate_pdf_report():
    """Generar informe PDF con estadísticas del sistema"""
    # Datos de ejemplo - en un sistema real estos vendrían de la base de datos
    report_data = ReportData(
        frequent_routes=[
            {"route": "A → B → C", "frequency": 15},
            {"route": "D → E → F", "frequency": 10}
        ],
        top_clients=[
            {"client_id": "C001", "name": "Cliente 1", "orders": 12},
            {"client_id": "C002", "name": "Cliente 2", "orders": 8}
        ],
        top_nodes=[
            {"node_id": "N001", "type": "storage", "visits": 20},
            {"node_id": "N002", "type": "recharge", "visits": 15}
        ],
        storage_usage={"used": 65, "available": 35},
        recharge_usage={"used": 45, "available": 55}
    )
    
    # Crear el PDF
    filename = f"drone_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Título
    elements.append(Paragraph("Reporte del Sistema de Drones", styles["Title"]))
    elements.append(Spacer(1, 12))
    
    # Rutas frecuentes
    elements.append(Paragraph("Rutas más frecuentes:", styles["Heading2"]))
    route_data = [["Ruta", "Frecuencia"]] + [[r["route"], r["frequency"]] for r in report_data.frequent_routes]
    route_table = Table(route_data)
    route_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(route_table)
    elements.append(Spacer(1, 12))
    
    # Más secciones del reporte...
    
    doc.build(elements)
    
    return FileResponse(filename, media_type='application/pdf', filename=filename)