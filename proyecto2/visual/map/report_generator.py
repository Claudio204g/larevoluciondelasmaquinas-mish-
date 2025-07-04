from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import tempfile
import matplotlib.pyplot as plt
from io import BytesIO

class ReportGenerator:
    """Clase para generar informes PDF con estadísticas del sistema."""
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.styles = getSampleStyleSheet()
    
    def generate_route_report(self):
        """Genera un informe PDF con las rutas más frecuentes."""
        # Crear documento PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        elements = []
        
        # Título
        elements.append(Paragraph("Informe de Rutas - Sistema de Drones", self.styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Datos básicos
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Rutas más frecuentes
        elements.append(Paragraph("Rutas Más Frecuentes", self.styles['Heading2']))
        
        frequent_routes = self.simulation.avl_routes.get_most_frequent(10)
        routes_data = [["Ruta", "Frecuencia"]]
        for route in frequent_routes:
            routes_data.append([route.key, str(route.value)])
        
        routes_table = Table(routes_data)
        routes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(routes_table)
        elements.append(Spacer(1, 24))
        
        # Estadísticas generales
        elements.append(Paragraph("Estadísticas Generales", self.styles['Heading2']))
        
        stats = self.simulation.get_simulation_stats()
        stats_data = [
            ["Nodos totales", stats['total_nodes']],
            ["Aristas totales", stats['total_edges']],
            ["Clientes registrados", stats['total_clients']],
            ["Órdenes totales", stats['total_orders']],
            ["Órdenes completadas", stats['completed_orders']],
            ["Órdenes pendientes", stats['pending_orders']]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 24))
        
        # Gráfico de distribución de nodos
        elements.append(Paragraph("Distribución de Nodos", self.styles['Heading2']))
        
        node_types = {
            "Almacenamiento": len([v for v in self.simulation.graph.vertices.values() 
                                 if v.vertex_type.value == "storage"]),
            "Recarga": len([v for v in self.simulation.graph.vertices.values() 
                          if v.vertex_type.value == "recharge"]),
            "Cliente": len([v for v in self.simulation.graph.vertices.values() 
                          if v.vertex_type.value == "client"])
        }
        
        # Crear gráfico y guardar en buffer
        fig, ax = plt.subplots()
        ax.pie(node_types.values(), labels=node_types.keys(), autopct='%1.1f%%')
        ax.set_title("Distribución de Tipos de Nodos")
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)
        
        elements.append(Image(img_buffer, width=400, height=300))
        
        # Construir documento
        doc.build(elements)
        
        return temp_file.name
    
    def generate_client_report(self, client_id):
        """Genera un informe PDF para un cliente específico."""
        # Implementación similar a generate_route_report pero enfocada en un cliente
        pass