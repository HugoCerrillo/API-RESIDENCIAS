import os
from fpdf import FPDF
from datetime import datetime, timedelta
from flask import current_app

class PDF_Base(FPDF):
    def get_logos(self):
        # Usamos current_app.root_path para llegar a la carpeta static
        # La estructura es: proyecto/app/services/pdf_service.py
        # El root_path de flask suele ser proyecto/app/
        static_path = os.path.join(current_app.root_path, '..', 'static', 'logos')
        
        return {
            "sep": os.path.join(static_path, 'sep.png'),
            "tecnm": os.path.join(static_path, 'tecnm.jpg'),
            "itl": os.path.join(static_path, 'itl.png'),
            "exper": os.path.join(static_path, 'ExperTrack.png')
        }

class PDF_Inventario(PDF_Base):
    def header(self):
        logos = self.get_logos()
        try:
            self.image(logos["sep"], 10, 10, 35)
            self.image(logos["tecnm"], 55, 10, 35)
            self.image(logos["itl"], 110, 8, 28)
            self.image(logos["exper"], 155, 10, 45)
        except Exception as e:
            print(f"Error cargando logos en Inventario: {e}")

        self.ln(35)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'INVENTARIO GENERAL DE EQUIPO TECNOLÓGICO', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'ExperTrack - Sistema de Control de Activos', 0, 1, 'C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        fecha_gen = (datetime.utcnow() + timedelta(hours=-6)).strftime("%d/%m/%Y %H:%M")
        self.cell(60, 10, f'Generado el: {fecha_gen}', 0, 0, 'L')
        self.cell(70, 10, '© 2026 ExperTrack - Todos los derechos reservados', 0, 0, 'C')
        self.cell(60, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'R')



class PDF_Expediente(PDF_Base):
    def header(self):
        logos = self.get_logos()
        try:
            self.image(logos["sep"], 10, 10, 35 )
            self.image(logos["tecnm"], 55, 10, 35)
            self.image(logos["itl"], 110, 8, 28)
            self.image(logos["exper"], 155, 10, 45)
        except Exception as e:
            print(f"Error al cargar logos en PDF: {e}")

        self.ln(35)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'EXPEDIENTE TÉCNICO DE EQUIPO', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'Sistema Gestor de Mantenimiento ExperTrack', 0, 1, 'C')
        self.ln(10)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        fecha_gen = (datetime.utcnow() + timedelta(hours=-6)).strftime("%d/%m/%Y %H:%M")
        self.cell(60, 10, f'Fecha: {fecha_gen}', 0, 0, 'L')
        self.cell(70, 10, '© 2026 ExperTrack - Todos los derechos reservados', 0, 0, 'C')
        self.cell(60, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'R')

def generar_inventario_pdf(equipos, usuario_gen):
    pdf = PDF_Inventario()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, f"Reporte generado por: {usuario_gen.nombre} {usuario_gen.apellido_paterno} ({usuario_gen.rol})", 0, 1, 'L')
    pdf.ln(5)

    # Encabezados
    pdf.set_fill_color(80, 75, 56); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(35, 10, 'Cód. Inventario', 1, 0, 'C', fill=True)
    pdf.cell(25, 10, 'Tipo', 1, 0, 'C', fill=True)
    pdf.cell(50, 10, 'Marca / Modelo', 1, 0, 'C', fill=True)
    pdf.cell(50, 10, 'Área / Ubicación', 1, 0, 'C', fill=True)
    pdf.cell(30, 10, 'Estado', 1, 1, 'C', fill=True)

    pdf.set_text_color(0, 0, 0); pdf.set_font('Helvetica', '', 8)
    for e in equipos:
        marca_modelo = f"{e.marca or ''} {e.modelo or ''}"
        area_ubic = e.area or "N/A"
        lineas_marca = pdf.multi_cell(50, 6, marca_modelo, split_only=True)
        lineas_area = pdf.multi_cell(50, 6, area_ubic, split_only=True)
        max_lineas = max(len(lineas_marca), len(lineas_area))
        h = max_lineas * 6
        if h < 8: h = 8

        pdf.cell(35, h, e.codigo_inventario or "N/A", 1, 0, 'C')
        pdf.cell(25, h, e.tipo_equipo or "N/A", 1, 0, 'C')
        
        curr_x, curr_y = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(50, h/len(lineas_marca) if lineas_marca else h, marca_modelo, 1, 'C')
        pdf.set_xy(curr_x + 50, curr_y)
        
        curr_x, curr_y = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(50, h/len(lineas_area) if lineas_area else h, area_ubic, 1, 'C')
        pdf.set_xy(curr_x + 50, curr_y)
        
        pdf.cell(30, h, e.estado_operativo or "N/A", 1, 1, 'C')

    return pdf.output()

def generar_expediente_pdf(equipo, spec, historial):
    pdf = PDF_Expediente()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Identificación
    pdf.set_font('Helvetica', 'B', 12); pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, '  IDENTIFICACIÓN DEL EQUIPO', 0, 1, 'L', fill=True)
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 10)
    col1, col2 = 40, 60
    datos = [
        ('Código Inventario:', equipo.codigo_inventario, 'Marca:', equipo.marca),
        ('No. de Serie:', equipo.numero_serie, 'Modelo:', equipo.modelo),
        ('Tipo de Equipo:', equipo.tipo_equipo, 'Área:', equipo.area),
        ('Ubicación:', equipo.ubicacion, 'Estado:', equipo.estado_operativo)
    ]
    for d in datos:
        pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, str(d[0]), 0)
        pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, str(d[1] or "N/A"), 0)
        pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, str(d[2]), 0)
        pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, str(d[3] or "N/A"), 0)
        pdf.ln()

    # Especificaciones
    if spec:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 8, '  ESPECIFICACIONES TÉCNICAS', 0, 1, 'L', fill=True)
        pdf.ln(2)
        specs = [('CPU:', spec.procesador, 'S.O:', spec.sistema_operativo), ('RAM:', f"{spec.ram} {spec.tipo_ram}", 'Disco:', f"{spec.almacenamiento} {spec.almacenamiento_tipo}")]
        for s in specs:
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, s[0], 0); pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, s[1], 0)
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, s[2], 0); pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, s[3], 0); pdf.ln()

    # Historial
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 8, '  HISTORIAL DE MANTENIMIENTOS', 0, 1, 'L', fill=True)
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9); pdf.set_fill_color(220, 220, 220)
    pdf.cell(25, 8, 'Fecha', 1, 0, 'C', fill=True)
    pdf.cell(40, 8, 'Técnico', 1, 0, 'C', fill=True)
    pdf.cell(30, 8, 'Tipo', 1, 0, 'C', fill=True)
    pdf.cell(95, 8, 'Descripción', 1, 1, 'C', fill=True)

    pdf.set_font('Helvetica', '', 8)
    for ev, tec, mant in historial:
        desc = mant.descripcion_trabajo if mant else ev.falla_reportada or "Sin descripción"
        lineas = pdf.multi_cell(95, 6, desc, split_only=True)
        h = len(lineas) * 6 if lineas else 8
        if h < 8: h = 8
        y_ini = pdf.get_y()
        pdf.cell(25, h, ev.fecha_creacion.strftime("%d/%m/%Y"), 1, 0, 'C')
        pdf.cell(40, h, f"{tec.nombre} {tec.apellido_paterno}"[:22], 1, 0, 'C')
        pdf.cell(30, h, mant.tipo if mant else "Evento", 1, 0, 'C')
        pdf.multi_cell(95, h/len(lineas) if lineas else h, desc, 1, 'L')
        pdf.set_xy(10, y_ini + h)

    return pdf.output()
