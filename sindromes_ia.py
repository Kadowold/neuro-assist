import streamlit as st
import datetime
import base64

def reconocimiento_sindromes(db):
    st.header("Reconocimiento de Sindromes Geneticos con IA")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            🧬 Vision IA — Analisis de rasgos fenotipicos
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Sube una fotografia del paciente. La IA analiza rasgos fenotipicos
            y sugiere posibles sindromes geneticos a considerar en el diagnostico.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("IMPORTANTE: Esta herramienta es unicamente de apoyo clinico. No reemplaza el criterio del genetista ni las pruebas geneticas confirmatorias. Usar con consentimiento informado del tutor legal.")
    st.divider()

    tab1, tab2 = st.tabs(["🔬 Nuevo analisis", "📋 Analisis guardados"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="sind_paciente")
            edad = st.number_input("Edad (meses)", min_value=0, max_value=216, value=12)
            sexo = st.radio("Sexo", ["Masculino", "Femenino"], horizontal=True)
        with col2:
            antecedentes_familiares = st.text_area(
                "Antecedentes familiares",
                placeholder="Consanguinidad, familiares con sindromes, malformaciones...",
                height=80
            )
            hallazgos_clinicos = st.text_area(
                "Hallazgos clinicos adicionales",
                placeholder="Cardiopatia, hipotonia, retraso del desarrollo, dismorfias conocidas...",
                height=80
            )

        st.divider()
        st.subheader("Fotografia del paciente")
        st.info("Sube una fotografia de frente del rostro del paciente con buena iluminacion.")

        imagen = st.file_uploader(
            "Seleccionar fotografia",
            type=["jpg", "jpeg", "png"],
            help="Fotografia frontal del rostro con buena iluminacion"
        )

        if imagen:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(imagen, caption="Fotografia cargada", use_column_width=True)

            if st.button("Analizar rasgos con Vision IA", use_container_width=True):
                if not paciente:
                    st.warning("Ingresa el nombre del paciente.")
                else:
                    with st.spinner("Analizando rasgos fenotipicos con Vision IA..."):
                        try:
                            import anthropic
                            api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
                            cliente = anthropic.Anthropic(api_key=api_key)

                            imagen_bytes = imagen.read()
                            imagen_b64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")

                            prompt = f"""Eres un genetista clinico y dismorfolog experto con amplia experiencia en sindromes geneticos pediatricos.

Analiza los rasgos fenotipicos visibles en esta imagen de un paciente con los siguientes datos:

PACIENTE: {paciente} | EDAD: {edad} meses | SEXO: {sexo}
ANTECEDENTES FAMILIARES: {antecedentes_familiares if antecedentes_familiares else 'No especificados'}
HALLAZGOS CLINICOS: {hallazgos_clinicos if hallazgos_clinicos else 'No especificados'}

Analiza sistematicamente:

## DESCRIPCION DISMORFOLOGICA
Describe detalladamente los rasgos faciales observables:
- Cabeza y craneo (forma, tamano)
- Frente (alta, prominente, estrecha)
- Ojos (distancia intercantal, forma, inclinacion palpebral, epicanto)
- Nariz (puente, columela, narinas)
- Orejas (posicion, forma, tamano)
- Boca y labios (grosor, forma)
- Mandibula y menton
- Cuello
- Expresion y tono facial

## RASGOS DISMORFICOS IDENTIFICADOS
Lista de hallazgos que se desvian de la normalidad.

## DIAGNOSTICO DIFERENCIAL DE SINDROMES
Basandote en los rasgos observados, considera:

### 1er Sindrome a considerar — [Nombre] — Probabilidad: ALTA/MEDIA/BAJA
- Rasgos que coinciden con este sindrome
- Rasgos que no coinciden
- Prevalencia: [frecuencia del sindrome]
- Herencia: [tipo de herencia]

### 2do Sindrome a considerar [si aplica]
[mismo formato]

### 3er Sindrome a considerar [si aplica]
[mismo formato]

## ESTUDIOS GENETICOS RECOMENDADOS
Pruebas especificas segun los sindromes considerados:
- Cariotipo
- Array CGH / microarray
- Paneles geneticos especificos
- Estudios metabolicos
- Otros

## EVALUACIONES COMPLEMENTARIAS
Especialidades a consultar y estudios adicionales.

## CONSIDERACIONES IMPORTANTES
Limitaciones del analisis y proximos pasos.

RECORDATORIO: Este es un analisis de apoyo. El diagnostico definitivo requiere evaluacion por genetista clinico y confirmacion molecular."""

                            respuesta = cliente.messages.create(
                                model="claude-opus-4-6",
                                max_tokens=3000,
                                messages=[{
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": "image/jpeg",
                                                "data": imagen_b64
                                            }
                                        },
                                        {
                                            "type": "text",
                                            "text": prompt
                                        }
                                    ]
                                }]
                            )

                            resultado = respuesta.content[0].text
                            st.session_state.sindromes_resultado = resultado
                            st.session_state.sindromes_paciente = paciente

                        except Exception as e:
                            st.error(f"Error al analizar: {e}")

        if "sindromes_resultado" in st.session_state:
            st.divider()
            st.subheader(f"Analisis fenotipico — {st.session_state.get('sindromes_paciente', '')}")
            st.markdown(st.session_state.sindromes_resultado)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Guardar analisis", use_container_width=True):
                    try:
                        db.collection("sindromes_ia").add({
                            "paciente": paciente,
                            "edad_meses": edad,
                            "sexo": sexo,
                            "hallazgos": hallazgos_clinicos,
                            "resultado": st.session_state.sindromes_resultado,
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
                        pdf.set_font("Helvetica", "B", 14)
                        pdf.cell(0, 18, "NeuroApp - Analisis Fenotipico Genetico", ln=True, align="C")
                        pdf.set_font("Helvetica", "", 10)
                        pdf.set_text_color(139, 163, 204)
                        pdf.cell(0, 10, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True, align="C")
                        pdf.ln(5)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Helvetica", "B", 10)
                        pdf.cell(0, 7, f"Paciente: {paciente} | Edad: {edad} meses | Sexo: {sexo}", ln=True)
                        pdf.ln(3)
                        pdf.set_font("Helvetica", "", 9)
                        for linea in st.session_state.sindromes_resultado.split("\n"):
                            linea_limpia = linea.replace("##", "").replace("**", "").strip()
                            if linea_limpia:
                                pdf.multi_cell(0, 5, linea_limpia)
                        pdf_bytes = bytes(pdf.output())
                        st.download_button(
                            label="Descargar PDF",
                            data=pdf_bytes,
                            file_name=f"sindromes_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error PDF: {e}")

    with tab2:
        buscar = st.text_input("Buscar por paciente", key="sind_buscar")
        if buscar:
            try:
                docs = db.collection("sindromes_ia").where("paciente", "==", buscar).stream()
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
                    st.info("Sin analisis para ese paciente.")
                else:
                    for item in lista:
                        with st.expander(f"Analisis {item.get('fecha','')} — {item.get('edad_meses','')} meses"):
                            st.markdown(item.get("resultado", ""))
            except Exception as e:
                st.error(f"Error: {e}")
