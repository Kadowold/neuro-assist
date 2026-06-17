import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

@st.cache_data(ttl=300)
def obtener_todos_cached(_db, coleccion):
    try:
        docs = _db.collection(coleccion).stream()
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

def dashboard_general(db):
    st.header("Dashboard General")
    st.markdown("> Estadisticas globales de todos los pacientes.")
    st.divider()

    with st.spinner("Cargando datos..."):
        sintomas = obtener_todos(db, "sintomas")
        calculadoras = obtener_todos(db, "calculadoras")
        triaje = obtener_todos(db, "triaje")
        desarrollo = obtener_todos(db, "desarrollo")
        crecimiento = obtener_todos(db, "crecimiento")
        dosis = obtener_todos(db, "dosis")
        eeg_lista = obtener_todos(db, "eeg")

    total_pacientes = len(set(
        [s.get("paciente", "") for s in sintomas] +
        [c.get("paciente", "") for c in calculadoras] +
        [t.get("paciente", "") for t in triaje]
    ))
    total_registros = len(sintomas) + len(calculadoras) + len(triaje) + len(desarrollo) + len(crecimiento) + len(dosis) + len(eeg_lista)

    # Metricas principales
    st.subheader("Resumen general")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Pacientes", total_pacientes)
    col2.metric("Sintomas", len(sintomas))
    col3.metric("Calculadoras", len(calculadoras))
    col4.metric("Pediatria", len(triaje) + len(desarrollo) + len(crecimiento) + len(dosis))
    col5.metric("EEG", len(eeg_lista))
    st.divider()

    # Tabs de analisis
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Sintomas",
        "📊 Calculadoras",
        "👶 Pediatria",
        "🔬 EEG"
    ])

    with tab1:
        if not sintomas:
            st.info("Sin datos de sintomas aun.")
        else:
            df = pd.DataFrame(sintomas)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sintomas mas frecuentes")
                if "tipo_sintoma" in df.columns:
                    conteo = df["tipo_sintoma"].value_counts().reset_index()
                    conteo.columns = ["tipo_sintoma", "count"]
                    fig = px.bar(conteo, x="tipo_sintoma", y="count",
                                color="tipo_sintoma",
                                labels={"tipo_sintoma": "Sintoma", "count": "Frecuencia"})
                    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                    font=dict(color="white"), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Desencadenantes mas comunes")
                if "desencadenante" in df.columns:
                    fig = px.pie(df, names="desencadenante")
                    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                    font=dict(color="white"))
                    st.plotly_chart(fig, use_container_width=True)

            st.subheader("Intensidad promedio por tipo de sintoma")
            if "tipo_sintoma" in df.columns and "intensidad" in df.columns:
                df["intensidad"] = pd.to_numeric(df["intensidad"], errors="coerce")
                promedio = df.groupby("tipo_sintoma")["intensidad"].mean().reset_index()
                promedio.columns = ["tipo_sintoma", "intensidad_promedio"]
                fig = px.bar(promedio, x="tipo_sintoma", y="intensidad_promedio",
                            color="intensidad_promedio",
                            color_continuous_scale=["#4fc3f7", "#f4a261", "#e63946"],
                            labels={"tipo_sintoma": "Sintoma", "intensidad_promedio": "Intensidad promedio"})
                fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Registros por fecha")
            if "fecha" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                por_fecha = df.groupby("fecha").size().reset_index(name="registros")
                fig = px.line(por_fecha, x="fecha", y="registros", markers=True,
                            color_discrete_sequence=["#4fc3f7"])
                fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if not calculadoras:
            st.info("Sin datos de calculadoras aun.")
        else:
            df = pd.DataFrame(calculadoras)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Escalas mas utilizadas")
                if "escala" in df.columns:
                    conteo = df["escala"].value_counts().reset_index()
                    conteo.columns = ["escala", "count"]
                    fig = px.pie(conteo, names="escala", values="count")
                    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                    font=dict(color="white"))
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Puntaje promedio por escala")
                if "escala" in df.columns and "puntaje" in df.columns:
                    df["puntaje"] = pd.to_numeric(df["puntaje"], errors="coerce")
                    promedio = df.groupby("escala")["puntaje"].mean().reset_index()
                    fig = px.bar(promedio, x="escala", y="puntaje",
                                color="escala",
                                labels={"escala": "Escala", "puntaje": "Puntaje promedio"})
                    fig.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                                    font=dict(color="white"), showlegend=False)
