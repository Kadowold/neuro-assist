import sqlite3
from fpdf import FPDF

def crear_conexion():
    conexion = sqlite3.connect("neuroapp.db")
    return conexion

def crear_tabla():
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sintomas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            tipo_sintoma TEXT NOT NULL,
            intensidad INTEGER NOT NULL,
            duracion INTEGER NOT NULL,
            desencadenante TEXT,
            notas TEXT
        )
    """)
    conexion.commit()
    conexion.close()
    from fpdf import FPDF

def generar_pdf(nombre_paciente, datos):
    pdf = FPDF()
    pdf.add_page()

    # Titulo
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "NeuroApp - Reporte de Sintomas", ln=True, align="C")
    pdf.ln(5)

    # Paciente
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Paciente: {nombre_paciente}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Total de registros: {len(datos)}", ln=True)
    pdf.ln(5)

    # Encabezados de tabla
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 8, "Fecha", border=1, fill=True)
    pdf.cell(35, 8, "Sintoma", border=1, fill=True)
    pdf.cell(22, 8, "Intensidad", border=1, fill=True)
    pdf.cell(25, 8, "Duracion", border=1, fill=True)
    pdf.cell(45, 8, "Desencadenante", border=1, fill=True)
    pdf.cell(0, 8, "Notas", border=1, fill=True, ln=True)

    # Filas
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for _, fila in datos.iterrows():
        pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(30, 7, str(fila["fecha"]), border=1, fill=fill)
        pdf.cell(35, 7, str(fila["tipo_sintoma"]), border=1, fill=fill)
        pdf.cell(22, 7, str(fila["intensidad"]) + "/10", border=1, fill=fill)
        pdf.cell(25, 7, str(fila["duracion"]) + " min", border=1, fill=fill)
        pdf.cell(45, 7, str(fila["desencadenante"]), border=1, fill=fill)
        pdf.cell(0, 7, str(fila["notas"]) if fila["notas"] else "-", border=1, fill=fill, ln=True)
        fill = not fill

    return pdf