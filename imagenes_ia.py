import streamlit as st
import datetime
import base64

def analizar_imagen_medica(imagen_bytes, tipo_imagen, contexto_clinico):
    try:
        import anthropic
        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
        cliente = anthropic.Anthropic(api_key=api_key)

        imagen_b64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")

        prompts = {
            "Radiografia de torax": "Analiza esta radiografia de torax pediatrica. Describe: campos pulmonares, silueta cardiaca, mediastino, costillas y diafragma. Menciona hallazgos normales y anormales.",
            "Radiografia de craneo": "Analiza esta radiografia de craneo. Describe: suturas, densidad osea, silla turca, calcificaciones y cualquier hallazgo anormal.",
            "Fondo de ojo": "Analiza esta imagen de fondo de ojo. Describe: papila optica, vasos retinianos, macula y retina periferica. Busca signos de hipertension endocraneal, papiledema o alteraciones vasculares.",
            "Foto de piel/lesion": "Analiza esta imagen dermatologica. Describe: tipo de lesion, distribucion, color, bordes y caracteristicas. Sugiere diagnostico diferencial dermatologico.",
            "TAC de craneo": "Analiza esta imagen de TAC craneal. Describe: paraquima cerebral, ventrículos, surcos, estructuras de la fosa posterior y cualquier hallazgo patologico.",
            "Otro estudio": "Analiza esta imagen medica clinicamente. Describe todos los hallazgos relevantes de forma estructurada y profesional."
        }

        prompt_base = prompts.get(tipo_imagen, prompts["Otro estudio"])

        prompt_completo = f"""Eres un radiologo y medico especialista experto.

{prompt_base}

Contexto clinico del paciente: {contexto_clinico}

Genera un reporte radiologico/medico estructurado con:

## DESCRIPCION DE LA IMAGEN
Descripcion sistematica y detallada de todos los hallazgos visibles.

## HALLAZGOS NORMALES
Lista de estructuras dentro de parametros normales.

## HALLAZGOS ANORMALES
Lista de hallazgos patologicos o sospechosos con descripcion detallada.

## IMPRESION DIAGNOSTICA
Interpretacion clinica de los hallazgos.

## DIAGNOSTICO DIFERENCIAL
Posibles diagnosticos basados en los hallazgos imagenologicos.

## RECOMENDACIONES
Estudios complementarios o seguimiento sugerido.

IMPORTANTE: Este analisis es una herramienta de apoyo clinico. 
No reemplaza la interpretacion de un radiologo certificado."""

        respuesta = cliente.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
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
                        "text": prompt_completo
                    }
                ]
            }]
        )
        return respuesta.content[0].text
    except Exception as e:
        return f"Error al analizar imagen: {str(e)}"


def analizador_imagenes(db):
    st.header("Analizador de Imagenes Medicas con IA")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            🔬 Vision IA — Analisis de imagenes medicas
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Sube radiografias, TAC, fondo de ojo o fotos de lesiones.
            La IA genera un reporte medico detallado en segundos.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔬 Analizar imagen", "📋 Analisis guardados"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="img_paciente")
            tipo_imagen = st.selectbox("Tipo de imagen", [
                "Radiografia de torax",
                "Radiografia de craneo",
                "Fondo de ojo",
                "Foto de piel/lesion",
                "TAC de craneo",
                "Otro estudio"
            ])
        with col2:
            contexto = st.text_area(
                "Contexto clinico",
                placeholder="Edad, sintomas, motivo del estudio...",
                height=100
            )

        st.divider()
        imagen = st.file_uploader(
            "Sube la imagen medica",
            type=["jpg", "jpeg", "png", "webp"],
            help="Formatos: JPG, PNG, WEBP"
        )

        if imagen:
            st.image(imagen, caption=f"{tipo_imagen}", use_column_width=True)

            if st.button("🔬 Analizar con IA", use_container_width=True):
                if paciente == "":
                    st.warning("Ingresa el nombre del paciente.")
                else:
                    with st.spinner("Analizando imagen con Vision IA..."):
                        imagen_bytes = imagen.read()
                        resultado = analizar_imagen_medica(
                            imagen_bytes, tipo_imagen, contexto
                        )

                    st.divider()
                    st.subheader("Reporte de analisis")
                    st.markdown(resultado)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar analisis", use_container_width=True):
                            try:
                                db.collection("imagenes_ia").add({
                                    "paciente": paciente,
                                    "tipo_imagen": tipo_imagen,
                                    "contexto": contexto,
                                    "resultado": resultado,
                                    "medico": st.session_state.get("usuario", ""),
                                    "fecha": datetime.datetime.now()
                                })
                                st.success("Analisis guardado.")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with col2:
                        if st.button("📄 Descargar PDF", use_container_width=True):
                            try:
                                from fpdf import FPDF
                                pdf = FPDF()
                                pdf.add_page()
                                pdf.set_fill_color(10, 22, 40)
                                pdf.rect(0, 0, 210, 35, "F")
                                pdf.set_text_color(201, 168, 76)
                                pdf.set_font("Helvetica", "B", 16)
                                pdf.cell(0, 18, "NeuroApp - Analisis de Imagen Medica", ln=True, align="C")
                                pdf.set_font("Helvetica", "", 10)
                                pdf.set_text_color(139, 163, 204)
                                pdf.cell(0, 10, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
                                pdf.ln(5)
                                pdf.set_text_color(0, 0, 0)
                                pdf.set_font("Helvetica", "B", 11)
                                pdf.cell(0, 7, f"Paciente: {paciente}", ln=True)
                                pdf.cell(0, 7, f"Tipo: {tipo_imagen}", ln=True)
                                pdf.ln(3)
                                pdf.set_font("Helvetica", "", 9)
                                for linea in resultado.split("\n"):
                                    linea_limpia = linea.replace("##", "").replace("**", "").strip()
                                    if linea_limpia:
                                        pdf.multi_cell(0, 5, linea_limpia)
                                pdf_bytes = bytes(pdf.output())
                                st.download_button(
                                    label="Descargar PDF",
                                    data=pdf_bytes,
                                    file_name=f"imagen_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.error(f"Error PDF: {e}")

    with tab2:
        st.subheader("Analisis guardados")
        buscar = st.text_input("Buscar por paciente", key="img_buscar")
        if buscar:
            try:
                docs = db.collection("imagenes_ia").where(
                    "paciente", "==", buscar
                ).stream()
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
                        with st.expander(f"🔬 {item.get('tipo_imagen','')} — {item.get('fecha','')}"):
                            st.markdown(item.get("resultado", ""))
            except Exception as e:
                st.error(f"Error: {e}")
