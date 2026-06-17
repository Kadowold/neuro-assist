import streamlit as st
import datetime

def generador_recetas(db):
    st.header("Generador de Recetas Medicas con IA")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            📋 Generador de recetas profesionales con IA
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Genera recetas medicas completas y profesionales en PDF con firma digital.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["📝 Nueva receta", "📋 Recetas guardadas"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Datos del paciente")
            paciente = st.text_input("Nombre completo del paciente")
            edad = st.number_input("Edad", min_value=0, max_value=120, value=5)
            peso = st.number_input("Peso (kg)", min_value=0.5, max_value=150.0, value=20.0)
            alergias = st.text_input("Alergias conocidas", placeholder="Penicilina, AINES...")
        with col2:
            st.subheader("Datos del medico")
            medico = st.text_input("Nombre del medico", value=f"Dra. {st.session_state.get('usuario', '')}")
            cedula = st.text_input("Cedula profesional", value="12345678")
            especialidad = st.text_input("Especialidad", value="Pediatria")
            institucion = st.text_input("Institucion", value="Hospital La Raza")

        st.divider()
        st.subheader("Diagnostico y medicamentos")

        diagnostico = st.text_area(
            "Diagnostico",
            placeholder="Faringoamigdalitis aguda bacteriana..."
        )

        modo_receta = st.radio(
            "Modo de generacion",
            ["Escribir medicamentos manualmente", "Generar con IA segun diagnostico"],
            horizontal=True
        )

        if modo_receta == "Generar con IA segun diagnostico":
            sintomas_adicionales = st.text_area(
                "Sintomas y contexto clinico",
                placeholder="Fiebre 38.5C de 3 dias, odinofagia, exudado amigdalino..."
            )
            if st.button("Generar receta con IA", use_container_width=True):
                if not diagnostico or not paciente:
                    st.warning("Ingresa el diagnostico y nombre del paciente.")
                else:
                    with st.spinner("Generando receta con IA..."):
                        try:
                            import anthropic
                            api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
                            cliente = anthropic.Anthropic(api_key=api_key)
                            prompt = f"""Eres un medico pediatra experto. Genera una receta medica profesional para:

PACIENTE: {paciente} | EDAD: {edad} anos | PESO: {peso} kg
ALERGIAS: {alergias if alergias else 'Ninguna conocida'}
DIAGNOSTICO: {diagnostico}
SINTOMAS: {sintomas_adicionales}

Genera una receta con este formato exacto:

MEDICAMENTO 1:
- Nombre: [nombre comercial y generico]
- Dosis: [dosis exacta en mg/kg si aplica]
- Via: [oral/IV/topica]
- Frecuencia: [cada X horas]
- Duracion: [X dias]
- Indicaciones especiales: [con alimentos, agitar antes de usar, etc]

MEDICAMENTO 2: [si aplica]
[mismo formato]

INDICACIONES GENERALES:
- [lista de cuidados en casa]

SIGNOS DE ALARMA:
- [cuando regresar de urgencia]

SEGUIMIENTO:
- [cuando volver a consulta]

Basa la receta en guias clinicas actualizadas. Calcula dosis por peso cuando sea relevante."""

                            respuesta = cliente.messages.create(
                                model="claude-opus-4-6",
                                max_tokens=2000,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            st.session_state.receta_generada = respuesta.content[0].text
                            st.session_state.receta_diagnostico = diagnostico
                        except Exception as e:
                            st.error(f"Error: {e}")

            if "receta_generada" in st.session_state:
                st.divider()
                st.subheader("Receta generada")
                receta_editada = st.text_area(
                    "Edita si es necesario:",
                    value=st.session_state.receta_generada,
                    height=300
                )
                _generar_pdf_receta(paciente, edad, peso, alergias, medico,
                                   cedula, especialidad, institucion,
                                   diagnostico, receta_editada, db)
        else:
            medicamentos_texto = st.text_area(
                "Escribe los medicamentos y dosis",
                placeholder="""Amoxicilina 250mg/5ml
- Dosis: 40mg/kg/dia
- Frecuencia: cada 8 horas
- Duracion: 7 dias

Paracetamol 160mg/5ml
- Dosis: 15mg/kg/dosis
- Frecuencia: cada 6 horas si fiebre o dolor""",
                height=200
            )
            indicaciones = st.text_area(
                "Indicaciones generales",
                placeholder="Reposo relativo, hidratacion abundante, dieta blanda..."
            )
            if st.button("Generar PDF de receta", use_container_width=True):
                if not paciente or not diagnostico:
                    st.warning("Ingresa paciente y diagnostico.")
                else:
                    contenido = f"{medicamentos_texto}\n\nINDICACIONES:\n{indicaciones}"
                    _generar_pdf_receta(paciente, edad, peso, alergias, medico,
                                      cedula, especialidad, institucion,
                                      diagnostico, contenido, db)

    with tab2:
        buscar = st.text_input("Buscar recetas por paciente", key="rec_buscar")
        if buscar:
            try:
                docs = db.collection("recetas").where("paciente", "==", buscar).stream()
                lista = []
                for doc in docs:
                    d = doc.to_dict()
                    if "fecha" in d and d["fecha"]:
                        try:
                            d["fecha"] = d["fecha"].strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    lista.append(d)
                if not lista:
                    st.info("Sin recetas para ese paciente.")
                else:
                    st.success(f"Se encontraron {len(lista)} receta(s).")
                    for rec in lista:
                        with st.expander(f"Receta {rec.get('fecha','')} — {rec.get('diagnostico','')}"):
                            st.markdown(rec.get("contenido", ""))
            except Exception as e:
                st.error(f"Error: {e}")


def _generar_pdf_receta(paciente, edad, peso, alergias, medico,
                        cedula, especialidad, institucion,
                        diagnostico, contenido, db):
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()

        # Header con gradiente simulado
        pdf.set_fill_color(10, 22, 40)
        pdf.rect(0, 0, 210, 40, "F")
        pdf.set_fill_color(26, 58, 110)
        pdf.rect(0, 35, 210, 5, "F")

        # Logo y titulo
        pdf.set_text_color(201, 168, 76)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_xy(10, 8)
        pdf.cell(0, 10, "NeuroApp", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(139, 163, 204)
        pdf.set_xy(10, 20)
        pdf.cell(0, 8, "Sistema Medico Avanzado — Receta Medica")
        pdf.set_xy(10, 28)
        pdf.cell(0, 6, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)

        # Datos del medico
        pdf.set_fill_color(201, 168, 76)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "  DATOS DEL MEDICO", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.cell(95, 6, f"Medico: {medico}")
        pdf.cell(0, 6, f"Especialidad: {especialidad}", ln=True)
        pdf.cell(95, 6, f"Cedula: {cedula}")
        pdf.cell(0, 6, f"Institucion: {institucion}", ln=True)
        pdf.ln(4)

        # Datos del paciente
        pdf.set_fill_color(26, 58, 110)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "  DATOS DEL PACIENTE", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.cell(95, 6, f"Paciente: {paciente}")
        pdf.cell(0, 6, f"Edad: {edad} anos | Peso: {peso} kg", ln=True)
        pdf.cell(0, 6, f"Alergias: {alergias if alergias else 'Ninguna conocida'}", ln=True)
        pdf.ln(4)

        # Diagnostico
        pdf.set_fill_color(201, 168, 76)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "  DIAGNOSTICO", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.multi_cell(0, 6, diagnostico)
        pdf.ln(4)

        # Receta
        pdf.set_fill_color(26, 58, 110)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "  PRESCRIPCION", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.ln(3)
        for linea in contenido.split("\n"):
            linea_limpia = linea.replace("**", "").replace("##", "").strip()
            if linea_limpia:
                pdf.multi_cell(0, 5, linea_limpia)

        # Firma
        pdf.ln(10)
        pdf.set_draw_color(201, 168, 76)
        pdf.line(20, pdf.get_y(), 90, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(10, 22, 40)
        pdf.cell(0, 5, f"  {medico}", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"  Ced. Prof. {cedula} | {especialidad}", ln=True)

        # Footer
        pdf.set_y(-20)
        pdf.set_fill_color(10, 22, 40)
        pdf.rect(0, pdf.get_y(), 210, 20, "F")
        pdf.set_text_color(139, 163, 204)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 10, "Generado por NeuroApp — Sistema Medico Avanzado", align="C")

        pdf_bytes = bytes(pdf.output())

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Descargar receta PDF",
                data=pdf_bytes,
                file_name=f"receta_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col2:
            if st.button("Guardar en Firebase", use_container_width=True):
                try:
                    db.collection("recetas").add({
                        "paciente": paciente,
                        "diagnostico": diagnostico,
                        "contenido": contenido,
                        "medico": medico,
                        "cedula": cedula,
                        "fecha": datetime.datetime.now()
                    })
                    st.success("Receta guardada.")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.success("Receta lista para descargar.")
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")
