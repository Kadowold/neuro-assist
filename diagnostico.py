import streamlit as st
import datetime

def diagnostico_diferencial(db):
    st.header("Asistente de Diagnostico Diferencial con IA")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            🤖 IA Avanzada — Diagnostico diferencial
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Describe los sintomas del paciente y la IA sugiere posibles diagnosticos
            con probabilidades, criterios diagnosticos y plan de estudio.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔍 Nuevo diagnostico", "📋 Historico"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="dx_paciente")
            edad = st.number_input("Edad (años)", min_value=0, max_value=120, value=5)
            sexo = st.radio("Sexo", ["Masculino", "Femenino"], horizontal=True)
        with col2:
            especialidad = st.selectbox("Enfoque clinico", [
                "Neurologia pediatrica",
                "Neurologia adultos",
                "Pediatria general",
                "Urgencias pediatricas",
                "Psiquiatria infantil"
            ])
            tiempo_evolucion = st.selectbox("Tiempo de evolucion", [
                "Agudo (horas)",
                "Subagudo (dias)",
                "Cronico (semanas/meses)",
                "Recurrente"
            ])

        st.subheader("Descripcion clinica")
        sintomas_principales = st.text_area(
            "Sintomas principales",
            placeholder="Ej: Cefalea intensa de inicio subito, nauseas, vomitos en proyectil, fotofobia...",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            signos_vitales = st.text_area(
                "Signos vitales",
                placeholder="FC: 110, FR: 28, Temp: 38.5, SatO2: 96%, TA: 100/60",
                height=80
            )
            antecedentes = st.text_area(
                "Antecedentes relevantes",
                placeholder="Epilepsia familiar, traumatismo previo, vacunas...",
                height=80
            )
        with col2:
            exploracion = st.text_area(
                "Hallazgos en exploracion fisica",
                placeholder="Rigidez de nuca, Kernig positivo, fontanela abombada...",
                height=80
            )
            estudios = st.text_area(
                "Estudios previos disponibles",
                placeholder="BH: leucocitosis, PCR elevada, TAC normal...",
                height=80
            )

        if st.button("🔍 Generar diagnostico diferencial con IA", use_container_width=True):
            if paciente == "" or sintomas_principales == "":
                st.warning("Ingresa el nombre del paciente y los sintomas principales.")
            else:
                with st.spinner("Analizando cuadro clinico con IA..."):
                    try:
                        import anthropic
                        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
                        cliente = anthropic.Anthropic(api_key=api_key)

                        prompt = f"""Eres un medico especialista en {especialidad} con amplia experiencia clinica.

Analiza el siguiente cuadro clinico y genera un diagnostico diferencial completo y estructurado:

PACIENTE: {paciente} | EDAD: {edad} años | SEXO: {sexo}
TIEMPO DE EVOLUCION: {tiempo_evolucion}
ESPECIALIDAD: {especialidad}

SINTOMAS PRINCIPALES: {sintomas_principales}
SIGNOS VITALES: {signos_vitales}
EXPLORACION FISICA: {exploracion}
ANTECEDENTES: {antecedentes}
ESTUDIOS PREVIOS: {estudios}

Genera un reporte con este formato exacto:

## DIAGNOSTICO DIFERENCIAL

### 1er LUGAR — [Diagnostico] — Probabilidad: ALTA/MEDIA/BAJA
**Justificacion:** Por que este diagnostico encaja con el cuadro
**Criterios a favor:** Lista de hallazgos que apoyan este diagnostico
**Criterios en contra:** Hallazgos que no encajan
**Accion inmediata:** Que hacer primero

### 2do LUGAR — [Diagnostico] — Probabilidad: ALTA/MEDIA/BAJA
[mismo formato]

### 3er LUGAR — [Diagnostico] — Probabilidad: ALTA/MEDIA/BAJA
[mismo formato]

### 4to LUGAR — [Diagnostico] — Probabilidad: BAJA
[mismo formato]

## DIAGNOSTICOS A DESCARTAR URGENTEMENTE
Lista de diagnosticos criticos que NO se pueden perder aunque sean menos probables.

## PLAN DE ESTUDIO SUGERIDO
Estudios de laboratorio e imagen ordenados por prioridad.

## SIGNOS DE ALARMA
Que cambios clinicos requieren atencion inmediata.

## TRATAMIENTO EMPIRICO INICIAL
Si aplica, mientras se confirma diagnostico.

Basa todo en evidencia medica actualizada y guias clinicas internacionales."""

                        respuesta = cliente.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=3000,
                            messages=[{"role": "user", "content": prompt}]
                        )

                        resultado = respuesta.content[0].text
                        st.session_state.dx_resultado = resultado
                        st.session_state.dx_paciente_actual = paciente

                    except Exception as e:
                        st.error(f"Error al generar diagnostico: {e}")

        if "dx_resultado" in st.session_state:
            st.divider()
            st.subheader(f"Diagnostico diferencial — {st.session_state.get('dx_paciente_actual', '')}")
            st.markdown(st.session_state.dx_resultado)
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar en Firebase", use_container_width=True):
                    try:
                        db.collection("diagnosticos").add({
                            "paciente": paciente,
                            "edad": edad,
                            "sexo": sexo,
                            "especialidad": especialidad,
                            "sintomas": sintomas_principales,
                            "resultado": st.session_state.dx_resultado,
                            "medico": st.session_state.get("usuario", ""),
                            "fecha": datetime.datetime.now()
                        })
                        st.success("Diagnostico guardado.")
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
                        pdf.cell(0, 18, "NeuroApp - Diagnostico Diferencial", ln=True, align="C")
                        pdf.set_font("Helvetica", "", 10)
                        pdf.set_text_color(139, 163, 204)
                        pdf.cell(0, 10, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
                        pdf.ln(5)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Helvetica", "B", 10)
                        pdf.cell(0, 7, f"Paciente: {paciente} | Edad: {edad} | Sexo: {sexo}", ln=True)
                        pdf.ln(3)
                        pdf.set_font("Helvetica", "", 9)
                        for linea in st.session_state.dx_resultado.split("\n"):
                            linea_limpia = linea.replace("##", "").replace("**", "").strip()
                            if linea_limpia:
                                pdf.multi_cell(0, 5, linea_limpia)
                        pdf_bytes = bytes(pdf.output())
                        st.download_button(
                            label="Descargar PDF",
                            data=pdf_bytes,
                            file_name=f"dx_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error PDF: {e}")

    with tab2:
        st.subheader("Diagnosticos anteriores")
        buscar = st.text_input("Buscar por paciente", key="dx_buscar")
        if buscar:
            try:
                docs = db.collection("diagnosticos").where("paciente", "==", buscar).stream()
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
                    st.info("Sin diagnosticos para ese paciente.")
                else:
                    for dx in lista:
                        with st.expander(f"🔍 {dx.get('especialidad','')} — {dx.get('fecha','')}"):
                            st.markdown(f"**Sintomas:** {dx.get('sintomas','')}")
                            st.markdown(dx.get("resultado", ""))
            except Exception as e:
                st.error(f"Error: {e}")
