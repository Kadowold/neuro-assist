import streamlit as st
import datetime
import pandas as pd

def obtener_datos_paciente(db, paciente):
    colecciones = {
        "sintomas": ["tipo_sintoma", "intensidad", "desencadenante", "fecha"],
        "calculadoras": ["escala", "puntaje", "interpretacion", "fecha"],
        "triaje": ["nivel_triaje", "fc", "fr", "temperatura", "sato2", "fecha"],
        "desarrollo": ["porcentaje", "interpretación", "edad", "fecha"],
        "crecimiento": ["peso_kg", "talla_cm", "imc", "peso_interpretacion", "fecha"],
        "eeg": ["estado", "interpretación", "picos_detectados", "fecha"],
        "signos_vitales": ["fc", "fr", "temperatura", "sato2", "estado_fc", "estado_fr", "fecha"],
    }

    datos_completos = {}
    for col, campos in colecciones.items():
        try:
            docs = db.collection(col).where("paciente", "==", paciente).stream()
            registros = []
            for doc in docs:
                d = doc.to_dict()
                registro = {}
                for campo in campos:
                    if campo in d:
                        val = d[campo]
                        if hasattr(val, 'strftime'):
                            val = val.strftime("%Y-%m-%d")
                        registro[campo] = val
                if registro:
                    registros.append(registro)
            datos_completos[col] = registros
        except:
            datos_completos[col] = []

    return datos_completos


def generar_prediccion_ia(paciente, datos, edad, sexo, antecedentes):
    try:
        import anthropic
        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
        cliente = anthropic.Anthropic(api_key=api_key)

        resumen_datos = f"""
PACIENTE: {paciente}
EDAD: {edad} años | SEXO: {sexo}
ANTECEDENTES FAMILIARES: {antecedentes}

HISTORIAL DE SINTOMAS NEUROLOGICOS ({len(datos['sintomas'])} registros):
{str(datos['sintomas'][:10]) if datos['sintomas'] else 'Sin registros'}

RESULTADOS DE ESCALAS CLINICAS ({len(datos['calculadoras'])} registros):
{str(datos['calculadoras'][:10]) if datos['calculadoras'] else 'Sin registros'}

HISTORIAL DE TRIAJE PEDIATRICO ({len(datos['triaje'])} registros):
{str(datos['triaje'][:5]) if datos['triaje'] else 'Sin registros'}

DESARROLLO INFANTIL ({len(datos['desarrollo'])} registros):
{str(datos['desarrollo'][:5]) if datos['desarrollo'] else 'Sin registros'}

CURVAS DE CRECIMIENTO ({len(datos['crecimiento'])} registros):
{str(datos['crecimiento'][:5]) if datos['crecimiento'] else 'Sin registros'}

ANALISIS EEG ({len(datos['eeg'])} registros):
{str(datos['eeg'][:5]) if datos['eeg'] else 'Sin registros'}

SIGNOS VITALES ({len(datos['signos_vitales'])} registros):
{str(datos['signos_vitales'][:5]) if datos['signos_vitales'] else 'Sin registros'}
"""

        prompt = f"""Eres un neurologo y pediatra experto en medicina basada en evidencia y prediccion de riesgos clinicos.

Analiza el siguiente historial medico completo de un paciente y genera un reporte de prediccion de riesgo neurologico detallado y profesional.

{resumen_datos}

Genera un reporte estructurado con las siguientes secciones en español:

## 1. RESUMEN CLINICO
Resumen conciso del estado actual del paciente basado en los datos disponibles.

## 2. RIESGOS NEUROLOGICOS IDENTIFICADOS
Lista de riesgos especificos con nivel (ALTO/MEDIO/BAJO) y justificación clinica basada en los datos.

## 3. PATRONES DETECTADOS
Patrones clinicos relevantes encontrados en el historial (frecuencia de sintomas, tendencias, correlaciones).

## 4. PREDICCION A CORTO PLAZO (1-3 meses)
Proyeccion clinica basada en tendencias actuales.

## 5. PREDICCION A LARGO PLAZO (6-12 meses)
Proyeccion de evolución probable si continua el patron actual.

## 6. FACTORES PROTECTORES
Aspectos positivos del historial que reducen riesgos.

## 7. RECOMENDACIONES CLINICAS PRIORITARIAS
Acciones concretas ordenadas por urgencia.

## 8. ESTUDIOS SUGERIDOS
Examenes complementarios recomendados segun el perfil de riesgo.

## 9. NIVEL DE RIESGO GLOBAL
Clasificacion final: BAJO / MODERADO / ALTO / CRITICO con justificacion.

Sé preciso, basate en evidencia medica y usa terminologia clinica profesional. 
Si los datos son insuficientes para alguna seccion, indicalo claramente."""

        respuesta = cliente.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        return respuesta.content[0].text

    except Exception as e:
        return f"Error al generar predicción: {str(e)}"


def predictor_riesgo(db):
    st.header("Predictor de Riesgo Neurologico con IA")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            🤖 IA Avanzada — Analisis predictivo
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Cruza todos los datos del paciente en Firebase y predice riesgos neurologicos futuros
            basandose en patrones clinicos y evidencia medica actualizada.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        paciente = st.text_input("Nombre del paciente", placeholder="Nombre exacto como esta en el sistema")
        edad = st.number_input("Edad del paciente (años)", min_value=0, max_value=120, value=5)
    with col2:
        sexo = st.radio("Sexo", ["Masculino", "Femenino"], horizontal=True)
        antecedentes = st.text_area(
            "Antecedentes familiares relevantes",
            placeholder="Epilepsia familiar, migranas, demencia, ACV...",
            height=100
        )

    st.divider()

    if st.button("🔍 Analizar y predecir riesgo con IA", use_container_width=True):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            with st.spinner("Recopilando datos del paciente desde Firebase..."):
                datos = obtener_datos_paciente(db, paciente)

            total_registros = sum(len(v) for v in datos.values())

            if total_registros == 0:
                st.warning("No se encontraron registros para este paciente. Registra datos primero.")
                return

            # Mostrar resumen de datos encontrados
            st.subheader("Datos encontrados")
            cols = st.columns(4)
            cols[0].metric("Sintomas", len(datos["sintomas"]))
            cols[1].metric("Escalas", len(datos["calculadoras"]))
            cols[2].metric("Pediatria", len(datos["triaje"]) + len(datos["desarrollo"]))
            cols[3].metric("EEG", len(datos["eeg"]))
            st.divider()

            with st.spinner("Analizando patrones y generando prediccion con IA... esto puede tardar unos segundos"):
                prediccion = generar_prediccion_ia(paciente, datos, edad, sexo, antecedentes)

            st.subheader("Reporte de Prediccion de Riesgo Neurologico")

            # Detectar nivel de riesgo para color
            nivel_color = "#40916c"
            if "ALTO" in prediccion.upper() and "NIVEL DE RIESGO GLOBAL" in prediccion.upper():
                nivel_color = "#e63946"
            elif "MODERADO" in prediccion.upper():
                nivel_color = "#f4a261"
            elif "CRITICO" in prediccion.upper():
                nivel_color = "#9b1c1c"

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0a1628, #0d1f3c);
                border: 1px solid {nivel_color}66;
                border-radius: 14px;
                padding: 24px;
                margin: 16px 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            ">
            </div>
            """, unsafe_allow_html=True)

            st.markdown(prediccion)

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar reporte en Firebase", use_container_width=True):
                    try:
                        db.collection("predicciones").add({
                            "paciente": paciente,
                            "edad": edad,
                            "sexo": sexo,
                            "antecedentes": antecedentes,
                            "total_registros_analizados": total_registros,
                            "predicción": predicción,
                            "medico": st.session_state.get("usuario", ""),
                            "fecha": datetime.datetime.now()
                        })
                        st.success("Reporte guardado en Firebase.")
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

            with col2:
                if st.button("📄 Descargar PDF", use_container_width=True):
                    try:
                        from fpdf import FPDF
                        pdf = FPDF()
                        pdf.add_page()

                        # Header
                        pdf.set_fill_color(10, 22, 40)
                        pdf.rect(0, 0, 210, 35, "F")
                        pdf.set_text_color(201, 168, 76)
                        pdf.set_font("Helvetica", "B", 18)
                        pdf.cell(0, 18, "NeuroApp - Predictor de Riesgo Neurologico", ln=True, align="C")
                        pdf.set_font("Helvetica", "", 10)
                        pdf.set_text_color(139, 163, 204)
                        pdf.cell(0, 10, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
                        pdf.ln(8)

                        # Datos del paciente
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.set_fill_color(201, 168, 76)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(0, 8, "DATOS DEL PACIENTE", ln=True, fill=True)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Helvetica", "", 10)
                        pdf.ln(2)
                        pdf.cell(60, 7, "Paciente:", border=0)
                        pdf.cell(0, 7, paciente, ln=True)
                        pdf.cell(60, 7, "Edad:", border=0)
                        pdf.cell(0, 7, f"{edad} anos", ln=True)
                        pdf.cell(60, 7, "Sexo:", border=0)
                        pdf.cell(0, 7, sexo, ln=True)
                        pdf.cell(60, 7, "Registros analizados:", border=0)
                        pdf.cell(0, 7, str(total_registros), ln=True)
                        pdf.ln(5)

                        # Reporte
                        pdf.set_fill_color(201, 168, 76)
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(0, 8, "REPORTE DE PREDICCION", ln=True, fill=True)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font("Helvetica", "", 9)
                        pdf.ln(3)
                        for linea in prediccion.split("\n"):
                            linea_limpia = linea.replace("##", "").replace("**", "").strip()
                            if linea_limpia:
                                pdf.multi_cell(0, 5, linea_limpia)

                        pdf_bytes = bytes(pdf.output())
                        st.download_button(
                            label="Descargar PDF del reporte",
                            data=pdf_bytes,
                            file_name=f"predicción_riesgo_{paciente}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")

    st.divider()

    # Historial de predicciones
    st.subheader("Predicciones anteriores")
    paciente_hist = st.text_input("Buscar predicciones por paciente", key="pred_hist")
    if paciente_hist:
        try:
            docs = db.collection("predicciones").where(
                "paciente", "==", paciente_hist
            ).stream()
            predicciones = []
            for doc in docs:
                d = doc.to_dict()
                if "fecha" in d and d["fecha"]:
                    try:
                        d["fecha"] = d["fecha"].strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                predicciones.append(d)

            if not predicciones:
                st.info("No se encontraron predicciones para ese paciente.")
            else:
                for pred in predicciones:
                    with st.expander(f"🔍 Predicción del {pred.get('fecha', '')} — {pred.get('total_registros_analizados', 0)} registros analizados"):
                        st.markdown(pred.get("predicción", ""))
        except Exception as e:
            st.error(f"Error: {e}")
