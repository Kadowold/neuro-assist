import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

def obtener_todos(db, coleccion):
    try:
        docs = db.collection(coleccion).stream()
        registros = []
        for doc in docs:
            d = doc.to_dict()
            if "fecha" in d and d["fecha"] is not None:
                try:
                    d["fecha"] = d["fecha"].date()
                except:
                    pass
            registros.append(d)
        return registros
    except:
        return []

def estadisticas_clinica(db):
    st.header("Estadisticas Predictivas de la Clinica")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600">
            📊 Inteligencia clinica — Proyecciones y tendencias
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Analiza patrones historicos y proyecta tendencias futuras de tu clinica.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.spinner("Cargando datos de la clinica..."):
        sintomas = obtener_todos(db, "sintomas")
        triaje = obtener_todos(db, "triaje")
        citas = obtener_todos(db, "agenda")
        dosis = obtener_todos(db, "dosis")
        eeg = obtener_todos(db, "eeg")
        diagnosticos = obtener_todos(db, "diagnosticos")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendencias",
        "🔮 Predicciones",
        "🏥 Carga clinica",
        "💊 Farmacologia"
    ])

    with tab1:
        st.subheader("Tendencias de la clinica")

        if sintomas:
            df = pd.DataFrame(sintomas)
            if "fecha" in df.columns and "tipo_sintoma" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                df["mes"] = df["fecha"].dt.to_period("M").astype(str)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Sintomas por mes**")
                    por_mes = df.groupby("mes").size().reset_index(name="total")
                    fig = px.line(por_mes, x="mes", y="total", markers=True,
                                color_discrete_sequence=["#c9a84c"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="#e8f0fe"))
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("**Sintomas mas frecuentes**")
                    conteo = df["tipo_sintoma"].value_counts().head(6).reset_index()
                    conteo.columns = ["sintoma", "count"]
                    fig = px.bar(conteo, x="count", y="sintoma", orientation="h",
                                color="count", color_continuous_scale=["#1a3a6e", "#c9a84c"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="#e8f0fe"))
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("**Intensidad promedio por mes**")
                if "intensidad" in df.columns:
                    df["intensidad"] = pd.to_numeric(df["intensidad"], errors="coerce")
                    intensidad_mes = df.groupby("mes")["intensidad"].mean().reset_index()
                    fig = px.area(intensidad_mes, x="mes", y="intensidad",
                                color_discrete_sequence=["#c9a84c"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="#e8f0fe"))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de sintomas aun.")

    with tab2:
        st.subheader("Proyecciones con IA")

        if sintomas:
            df = pd.DataFrame(sintomas)
            total = len(sintomas)
            pacientes_unicos = df["paciente"].nunique() if "paciente" in df.columns else 0

            if st.button("🔮 Generar proyecciones con IA", use_container_width=True):
                with st.spinner("Analizando datos y generando proyecciones..."):
                    try:
                        import anthropic
                        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
                        cliente = anthropic.Anthropic(api_key=api_key)

                        resumen = f"""
Datos de la clinica:
- Total sintomas registrados: {total}
- Pacientes unicos: {pacientes_unicos}
- Sintomas mas frecuentes: {df['tipo_sintoma'].value_counts().head(5).to_dict() if 'tipo_sintoma' in df.columns else 'N/A'}
- Desencadenantes: {df['desencadenante'].value_counts().head(5).to_dict() if 'desencadenante' in df.columns else 'N/A'}
- Total citas agendadas: {len(citas)}
- Total analisis EEG: {len(eeg)}
- Total diagnosticos: {len(diagnosticos)}
- Medicamentos mas usados: {pd.DataFrame(dosis)['medicamento'].value_counts().head(5).to_dict() if dosis else 'N/A'}
"""

                        prompt = f"""Eres un experto en epidemiologia clinica y gestion de servicios de salud.

Analiza estos datos de una clinica de neurologia pediatrica y genera un reporte de proyecciones:

{resumen}

Genera un reporte con estas secciones:

## ANALISIS ACTUAL
Estado actual de la clinica basado en los datos.

## PATRONES ESTACIONALES
Que enfermedades o sintomas podrian aumentar en proximas semanas/meses segun patrones conocidos en neurologia pediatrica.

## PROYECCION DE DEMANDA (proximo mes)
Estimacion de carga de pacientes y tipos de consultas esperadas.

## ENFERMEDADES EN TENDENCIA
Condiciones que muestran aumento en los registros actuales.

## RECOMENDACIONES PARA LA CLINICA
Acciones concretas para prepararse ante las proyecciones (insumos, personal, estudios).

## OPORTUNIDADES DE MEJORA
Areas donde la clinica puede optimizar su atencion basado en los datos.

Se preciso y practico. Basa las proyecciones en datos epidemiologicos reales de neurologia pediatrica."""

                        respuesta = cliente.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=2000,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.markdown(respuesta.content[0].text)

                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("Necesitas mas datos registrados para generar proyecciones.")

    with tab3:
        st.subheader("Carga clinica")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total consultas", len(sintomas) + len(diagnosticos))
        col2.metric("Citas agendadas", len(citas))
        col3.metric("EEG realizados", len(eeg))

        if triaje:
            df_t = pd.DataFrame(triaje)
            if "nivel_triaje" in df_t.columns:
                st.markdown("**Distribucion de urgencias en triaje**")
                conteo = df_t["nivel_triaje"].value_counts().reset_index()
                conteo.columns = ["nivel", "count"]
                colores = {
                    "VERDE - NO URGENTE": "#40916c",
                    "AMARILLO - SEMI-URGENCIA": "#f4a261",
                    "NARANJA - URGENCIA": "#e76f51",
                    "ROJO - EMERGENCIA": "#e63946"
                }
                fig = px.pie(conteo, names="nivel", values="count",
                            color="nivel", color_discrete_map=colores)
                fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                font=dict(color="#e8f0fe"))
                st.plotly_chart(fig, use_container_width=True)

        if citas:
            df_c = pd.DataFrame(citas)
            if "tipo_cita" in df_c.columns:
                st.markdown("**Tipos de cita mas frecuentes**")
                conteo = df_c["tipo_cita"].value_counts().reset_index()
                conteo.columns = ["tipo", "count"]
                fig = px.bar(conteo, x="tipo", y="count", color="tipo",
                            color_discrete_sequence=["#c9a84c", "#f0c96e", "#1a3a6e",
                                                    "#4fc3f7", "#e63946", "#40916c"])
                fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                font=dict(color="#e8f0fe"), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Farmacologia clinica")

        if dosis:
            df_d = pd.DataFrame(dosis)

            col1, col2 = st.columns(2)
            with col1:
                if "medicamento" in df_d.columns:
                    st.markdown("**Medicamentos mas calculados**")
                    conteo = df_d["medicamento"].value_counts().reset_index()
                    conteo.columns = ["medicamento", "count"]
                    fig = px.bar(conteo, x="medicamento", y="count",
                                color="medicamento",
                                color_discrete_sequence=["#c9a84c", "#f0c96e", "#1a3a6e",
                                                        "#4fc3f7", "#e63946"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="#e8f0fe"), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                if "peso" in df_d.columns:
                    st.markdown("**Distribucion de peso de pacientes**")
                    df_d["peso"] = pd.to_numeric(df_d["peso"], errors="coerce")
                    fig = px.histogram(df_d, x="peso", nbins=10,
                                    color_discrete_sequence=["#c9a84c"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="#e8f0fe"))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de medicamentos aun.")
