import streamlit as st
import datetime
import tempfile
import os

def transcribir_audio(archivo_audio):
    try:
        from openai import OpenAI
        api_key = st.secrets["OPENAI_API_KEY"]
        cliente = OpenAI(api_key=api_key)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(archivo_audio.getvalue())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            transcripcion = cliente.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="es",
                prompt="Transcripción medica en español. Terminos medicos, neurologicos y pediatricos."
            )

        os.unlink(tmp_path)
        return transcripcion.text

    except Exception as e:
        return f"Error al transcribir: {str(e)}"


def mejorar_nota_con_ia(texto_crudo, tipo_nota):
    try:
        import anthropic
        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
        cliente = anthropic.Anthropic(api_key=api_key)

        prompts = {
            "Nota de evolucion": f"""Eres un medico especialista. Toma este texto dictado y redactalo como una nota de evolución medica profesional y estructurada en español. 
            Usa el formato SOAP (Subjetivo, Objetivo, Analisis, Plan).
            Texto dictado: {texto_crudo}""",

            "Historia clinica": f"""Eres un medico especialista. Toma este texto dictado y redactalo como una historia clinica completa y profesional en español.
            Incluye secciones: Motivo de consulta, Antecedentes, Enfermedad actual, Exploración fisica, Diagnostico, Plan.
            Texto dictado: {texto_crudo}""",

            "Nota de urgencias": f"""Eres un medico de urgencias. Toma este texto dictado y redactalo como una nota de urgencias medica profesional en español.
            Incluye: Motivo, Signos vitales, Exploración, Diagnostico presuntivo, Manejo inicial.
            Texto dictado: {texto_crudo}""",

            "Resumen de consulta": f"""Eres un medico especialista. Toma este texto dictado y redactalo como un resumen de consulta medica claro y profesional en español.
            Texto dictado: {texto_crudo}""",

            "Solo transcripción": texto_crudo
        }

        if tipo_nota == "Solo transcripción":
            return texto_crudo

        respuesta = cliente.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompts[tipo_nota]}]
        )
        return respuesta.content[0].text

    except Exception as e:
        return f"Error al mejorar nota: {str(e)}"


def notas_por_voz(db):
    st.header("Notas Medicas por Voz")
    st.markdown("> Dicta tus notas medicas y la IA las transcribe y redacta profesionalmente.")
    st.divider()

    tab1, tab2 = st.tabs(["🎙️ Grabar nota", "📋 Notas guardadas"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="voz_paciente")
        with col2:
            tipo_nota = st.selectbox("Tipo de nota", [
                "Nota de evolución",
                "Historia clinica",
                "Nota de urgencias",
                "Resumen de consulta",
                "Solo transcripción"
            ])

        st.divider()
        st.subheader("Graba tu nota de voz")
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0a1628, #0d1f3c);
            border: 1px solid #c9a84c44;
            border-radius: 14px;
            padding: 24px;
            text-align: center;
            margin: 16px 0;
        ">
            <div style="font-size: 48px">🎙️</div>
            <div style="color: #8ba3cc; font-size: 14px; margin-top: 8px">
                Graba un audio desde tu dispositivo y subelo aqui
            </div>
            <div style="color: #c9a84c88; font-size: 12px; margin-top: 4px">
                Formatos soportados: WAV, MP3, M4A, OGG (max 25MB)
            </div>
        </div>
        """, unsafe_allow_html=True)

        archivo_audio = st.file_uploader(
            "Sube tu audio aqui",
            type=["wav", "mp3", "m4a", "ogg", "webm"],
            help="Graba desde tu celular o computadora y sube el archivo"
        )

        st.info("💡 En tu celular: usa la app de grabadora de voz, graba tu nota y sube el archivo. En computadora: usa cualquier grabadora de audio.")

        if archivo_audio:
            st.audio(archivo_audio)

            col1, col2 = st.columns(2)
            with col1:
                transcribir = st.button("🎙️ Transcribir audio", use_container_width=True)
            with col2:
                limpiar = st.button("🗑️ Limpiar", use_container_width=True)

            if limpiar:
                if "transcripcion_actual" in st.session_state:
                    del st.session_state.transcripcion_actual
                if "nota_mejorada" in st.session_state:
                    del st.session_state.nota_mejorada
                st.rerun()

            if transcribir:
                if paciente == "":
                    st.warning("Por favor ingresa el nombre del paciente.")
                else:
                    with st.spinner("Transcribiendo audio con Whisper AI..."):
                        transcripcion = transcribir_audio(archivo_audio)
                        st.session_state.transcripcion_actual = transcripcion

            if "transcripcion_actual" in st.session_state:
                st.divider()
                st.subheader("Transcripción")
                transcripcion_editada = st.text_area(
                    "Puedes editar la transcripción antes de mejorarla:",
                    value=st.session_state.transcripción_actual,
                    height=150,
                    key="trans_edit"
                )

                if st.button("✨ Mejorar con IA", use_container_width=True):
                    with st.spinner(f"Redactando {tipo_nota} con IA..."):
                        nota_mejorada = mejorar_nota_con_ia(transcripcion_editada, tipo_nota)
                        st.session_state.nota_mejorada = nota_mejorada

                if "nota_mejorada" in st.session_state:
                    st.divider()
                    st.subheader(f"Nota medica — {tipo_nota}")

                    nota_final = st.text_area(
                        "Nota generada (puedes editar antes de guardar):",
                        value=st.session_state.nota_mejorada,
                        height=300,
                        key="nota_final_edit"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar nota", use_container_width=True):
                            if paciente == "":
                                st.warning("Ingresa el nombre del paciente.")
                            else:
                                try:
                                    db.collection("notas_medicas").add({
                                        "paciente": paciente,
                                        "tipo_nota": tipo_nota,
                                        "transcripcion_original": st.session_state.transcripcion_actual,
                                        "nota_final": nota_final,
                                        "medico": st.session_state.get("usuario", ""),
                                        "fecha": datetime.datetime.now()
                                    })
                                    st.success("Nota guardada en Firebase.")
                                    del st.session_state.transcripcion_actual
                                    del st.session_state.nota_mejorada
                                except Exception as e:
                                    st.error(f"Error al guardar: {e}")

                    with col2:
                        # Descargar como PDF
                        if st.button("📄 Descargar PDF", use_container_width=True):
                            try:
                                from fpdf import FPDF
                                pdf = FPDF()
                                pdf.add_page()
                                pdf.set_fill_color(10, 22, 40)
                                pdf.rect(0, 0, 210, 30, "F")
                                pdf.set_text_color(201, 168, 76)
                                pdf.set_font("Helvetica", "B", 18)
                                pdf.cell(0, 15, "NeuroApp - Nota Medica", ln=True, align="C")
                                pdf.set_font("Helvetica", "", 10)
                                pdf.set_text_color(139, 163, 204)
                                pdf.cell(0, 10, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
                                pdf.ln(8)
                                pdf.set_text_color(0, 0, 0)
                                pdf.set_font("Helvetica", "B", 12)
                                pdf.cell(0, 8, f"Paciente: {paciente}", ln=True)
                                pdf.cell(0, 8, f"Tipo de nota: {tipo_nota}", ln=True)
                                pdf.cell(0, 8, f"Medico: {st.session_state.get('usuario', '')}", ln=True)
                                pdf.ln(5)
                                pdf.set_fill_color(10, 22, 40)
                                pdf.set_text_color(201, 168, 76)
                                pdf.set_font("Helvetica", "B", 11)
                                pdf.cell(0, 8, tipo_nota.upper(), ln=True, fill=True)
                                pdf.set_text_color(0, 0, 0)
                                pdf.set_font("Helvetica", "", 10)
                                pdf.ln(3)
                                for linea in nota_final.split("\n"):
                                    pdf.multi_cell(0, 6, linea)
                                pdf_bytes = bytes(pdf.output())
                                st.download_button(
                                    label="Descargar PDF",
                                    data=pdf_bytes,
                                    file_name=f"nota_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.error(f"Error al generar PDF: {e}")

        else:
            st.divider()
            st.subheader("O escribe directamente")
            texto_manual = st.text_area(
                "Escribe o pega el texto de tu nota aqui:",
                height=150,
                placeholder="Paciente de 5 años con fiebre de 38.5, sin signos meningeos..."
            )

            if texto_manual and st.button("✨ Mejorar texto con IA", use_container_width=True):
                if paciente == "":
                    st.warning("Por favor ingresa el nombre del paciente.")
                else:
                    with st.spinner("Redactando nota con IA..."):
                        nota_mejorada = mejorar_nota_con_ia(texto_manual, tipo_nota)
                        st.session_state.nota_mejorada = nota_mejorada
                        st.rerun()

    with tab2:
        st.subheader("Notas guardadas")
        paciente_buscar = st.text_input("Buscar notas por paciente", key="voz_buscar")

        if paciente_buscar:
            try:
                docs = db.collection("notas_medicas").where(
                    "paciente", "==", paciente_buscar
                ).stream()

                notas = []
                for doc in docs:
                    datos = doc.to_dict()
                    if "fecha" in datos and datos["fecha"]:
                        try:
                            datos["fecha"] = datos["fecha"].strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    notas.append(datos)

                if not notas:
                    st.info("No se encontraron notas para ese paciente.")
                else:
                    st.success(f"Se encontraron {len(notas)} nota(s).")
                    for nota in notas:
                        with st.expander(f"📋 {nota.get('tipo_nota', '')} — {nota.get('fecha', '')}"):
                            st.markdown(nota.get("nota_final", ""))
            except Exception as e:
                st.error(f"Error al buscar notas: {e}")
        else:
            st.info("Escribe el nombre del paciente para ver sus notas.")
