import streamlit as st
import datetime

MEDICAMENTOS_COMUNES = [
    "Paracetamol", "Ibuprofeno", "Amoxicilina", "Amoxicilina-Clavulanato",
    "Azitromicina", "Cetirizina", "Loratadina", "Salbutamol", "Prednisona",
    "Metoclopramida", "Dimenhidrinato", "Omeprazol", "Ranitidina",
    "Acido valproico", "Carbamazepina", "Fenitoina", "Levetiracetam",
    "Clonazepam", "Diazepam", "Metilfenidato", "Risperidona", "Haloperidol",
    "Fluoxetina", "Sertralina", "Amitriptilina", "Vitamina D", "Hierro",
    "Zinc", "Vitamina C", "Metronidazol", "Ciprofloxacino", "Trimetoprim",
    "Dexametasona", "Hidrocortisona", "Insulina", "Metformina", "Warfarina",
    "Aspirina", "Naproxeno", "Ketorolaco", "Morfina", "Tramadol",
    "Otro medicamento"
]

def buscador_interacciones(db):
    st.header("Buscador de Interacciones Farmacologicas")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            💊 Detector de interacciones farmacologicas con IA
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Selecciona hasta 5 medicamentos y la IA analiza combinaciones peligrosas,
            contraindicaciones y alternativas seguras.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        paciente = st.text_input("Nombre del paciente (opcional)")
        edad = st.number_input("Edad (años)", min_value=0, max_value=120, value=5)
        peso = st.number_input("Peso (kg)", min_value=0.5, max_value=150.0, value=20.0)
    with col2:
        condiciones = st.text_area(
            "Condiciones medicas del paciente",
            placeholder="Epilepsia, insuficiencia renal, hepatopatia...",
            height=100
        )

    st.divider()
    st.subheader("Selecciona los medicamentos")

    med1 = st.selectbox("Medicamento 1", ["Seleccionar..."] + MEDICAMENTOS_COMUNES)
    med2 = st.selectbox("Medicamento 2", ["Seleccionar..."] + MEDICAMENTOS_COMUNES)
    med3 = st.selectbox("Medicamento 3 (opcional)", ["Ninguno"] + MEDICAMENTOS_COMUNES)
    med4 = st.selectbox("Medicamento 4 (opcional)", ["Ninguno"] + MEDICAMENTOS_COMUNES)
    med5 = st.selectbox("Medicamento 5 (opcional)", ["Ninguno"] + MEDICAMENTOS_COMUNES)

    medicamentos_seleccionados = [m for m in [med1, med2, med3, med4, med5]
                                   if m not in ["Seleccionar...", "Ninguno"]]

    if med1 == "Otro medicamento" or med2 == "Otro medicamento":
        otros = st.text_input("Especifica medicamentos adicionales",
                             placeholder="Nombre del medicamento, dosis...")
        if otros:
            medicamentos_seleccionados.append(otros)

    if len(medicamentos_seleccionados) >= 2:
        if st.button("Analizar interacciones con IA", use_container_width=True):
            with st.spinner("Analizando interacciones farmacologicas..."):
                try:
                    import anthropic
                    api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
                    cliente = anthropic.Anthropic(api_key=api_key)

                    prompt = f"""Eres un farmacolo clinico y pediatra experto.

Analiza las interacciones farmacologicas entre estos medicamentos para el siguiente paciente:

PACIENTE: {paciente if paciente else 'No especificado'}
EDAD: {edad} años | PESO: {peso} kg
CONDICIONES MEDICAS: {condiciones if condiciones else 'No especificadas'}

MEDICAMENTOS A ANALIZAR:
{chr(10).join([f"- {m}" for m in medicamentos_seleccionados])}

Genera un reporte completo con:

## NIVEL DE RIESGO GLOBAL
SIN INTERACCIONES / INTERACCION MENOR / INTERACCION MODERADA / INTERACCION GRAVE / CONTRAINDICADO

## INTERACCIONES DETECTADAS
Para cada par de medicamentos que interactuan:
### [Medicamento A] + [Medicamento B]
- Tipo de interaccion: [farmacocinetica/farmacodinamica]
- Severidad: LEVE / MODERADA / GRAVE
- Mecanismo: explicacion del mecanismo
- Efecto clinico: que puede ocurrirle al paciente
- Manejo: como manejar esta interaccion

## CONTRAINDICACIONES ESPECIFICAS
Para la edad, peso y condiciones medicas del paciente.

## ALTERNATIVAS TERAPEUTICAS SEGURAS
Medicamentos alternativos si hay interacciones graves.

## RECOMENDACIONES CLINICAS
Ajustes de dosis, monitorizacion o cambios sugeridos.

## CONCLUSION
Resumen ejecutivo para el medico.

Basa el analisis en fuentes como Micromedex, Lexicomp y guias pediatricas actualizadas."""

                    respuesta = cliente.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=3000,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    resultado = respuesta.content[0].text
                    st.session_state.interacciones_resultado = resultado
                    st.session_state.interacciones_meds = medicamentos_seleccionados

                except Exception as e:
                    st.error(f"Error: {e}")

    elif len(medicamentos_seleccionados) == 1:
        st.info("Selecciona al menos 2 medicamentos para analizar interacciones.")

    if "interacciones_resultado" in st.session_state:
        st.divider()
        resultado = st.session_state.interacciones_resultado

        nivel_color = "#40916c"
        if "GRAVE" in resultado.upper():
            nivel_color = "#e63946"
        elif "MODERADA" in resultado.upper():
            nivel_color = "#f4a261"
        elif "CONTRAINDICADO" in resultado.upper():
            nivel_color = "#9b1c1c"

        st.markdown(f"""
        <div style="
            background: #0d1f3c;
            border-left: 6px solid {nivel_color};
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
        ">
            <div style="color: {nivel_color}; font-weight: 700; font-size: 14px">
                Medicamentos analizados: {' + '.join(st.session_state.interacciones_meds)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(resultado)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Guardar analisis", use_container_width=True):
                try:
                    db.collection("interacciones").add({
                        "paciente": paciente if paciente else "No especificado",
                        "medicamentos": medicamentos_seleccionados,
                        "resultado": resultado,
                        "medico": st.session_state.get("usuario", ""),
                        "fecha": datetime.datetime.now()
                    })
                    st.success("Analisis guardado.")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button("Descargar PDF", use_container_width=True):
                try:
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_fill_color(10, 22, 40)
                    pdf.rect(0, 0, 210, 35, "F")
                    pdf.set_text_color(201, 168, 76)
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.cell(0, 18, "NeuroApp - Interacciones Farmacologicas", ln=True, align="C")
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(139, 163, 204)
                    pdf.cell(0, 10, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True, align="C")
                    pdf.ln(5)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 7, f"Medicamentos: {', '.join(medicamentos_seleccionados)}", ln=True)
                    pdf.cell(0, 7, f"Paciente: {paciente} | Edad: {edad} | Peso: {peso}kg", ln=True)
                    pdf.ln(3)
                    pdf.set_font("Helvetica", "", 9)
                    for linea in resultado.split("\n"):
                        linea_limpia = linea.replace("##", "").replace("**", "").strip()
                        if linea_limpia:
                            pdf.multi_cell(0, 5, linea_limpia)
                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        label="Descargar",
                        data=pdf_bytes,
                        file_name=f"interacciones_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error PDF: {e}")
