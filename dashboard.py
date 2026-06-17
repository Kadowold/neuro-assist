import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

def obtener_todos(db, coleccion):
    try:
        docs = db.collection(coleccion).stream()
        registros = []
        for doc in docs:
            datos = doc.to_dict()
            if "fecha" in datos and datos["fecha"] is not None:
                try:
                    datos["fecha"] = datos["fecha"].date()
                except:
                    pass
            registros.append(datos)
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

    st.subheader("Resumen general")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Pacientes", total_pacientes)
    col2.metric("Sintomas", len(sintomas))
    col3.metric("Calculadoras", len(calculadoras))
    col4.metric("Pediatria", len(triaje) + len(desarrollo) + len(crecimiento) + len(dosis))
    col5.metric("EEG", len(eeg_lista))
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Sintomas",
        "Calculadoras",
        "Pediatria",
        "EEG"
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
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("Desencadenantes mas comunes")
                if "desencadenante" in df.columns:
                    fig = px.pie(df, names="desencadenante",
                                color_discrete_sequence=["#c9a84c", "#f0c96e", "#e07b2a",
                                                        "#d4a017", "#b8860b", "#f4a261"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"))
                    st.plotly_chart(fig, use_container_width=True)

            if "tipo_sintoma" in df.columns and "intensidad" in df.columns:
                st.subheader("Intensidad promedio por tipo de sintoma")
                df["intensidad"] = pd.to_numeric(df["intensidad"], errors="coerce")
                promedio = df.groupby("tipo_sintoma")["intensidad"].mean().reset_index()
                promedio.columns = ["tipo_sintoma", "intensidad_promedio"]
                fig = px.bar(promedio, x="tipo_sintoma", y="intensidad_promedio",
                            color="intensidad_promedio",
                            color_continuous_scale=["#1a3a6e", "#c9a84c", "#e63946"])
                fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
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
                    fig = px.pie(conteo, names="escala", values="count",
                                color_discrete_sequence=["#c9a84c", "#f0c96e", "#1a3a6e", "#4fc3f7"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"))
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("Puntaje promedio por escala")
                if "escala" in df.columns and "puntaje" in df.columns:
                    df["puntaje"] = pd.to_numeric(df["puntaje"], errors="coerce")
                    promedio = df.groupby("escala")["puntaje"].mean().reset_index()
                    fig = px.bar(promedio, x="escala", y="puntaje",
                                color="escala",
                                color_discrete_sequence=["#c9a84c", "#f0c96e", "#1a3a6e", "#4fc3f7"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Niveles de triaje")
            if triaje:
                df_t = pd.DataFrame(triaje)
                if "nivel_triaje" in df_t.columns:
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
                                    font=dict(color="white"))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de triaje.")
        with col2:
            st.subheader("Desarrollo infantil")
            if desarrollo:
                df_d = pd.DataFrame(desarrollo)
                if "interpretacion" in df_d.columns:
                    conteo = df_d["interpretacion"].value_counts().reset_index()
                    conteo.columns = ["interpretacion", "count"]
                    fig = px.bar(conteo, x="interpretacion", y="count",
                                color="interpretacion",
                                color_discrete_sequence=["#c9a84c", "#40916c", "#e63946"])
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de desarrollo.")

        if dosis:
            st.subheader("Medicamentos mas calculados")
            df_d = pd.DataFrame(dosis)
            if "medicamento" in df_d.columns:
                conteo = df_d["medicamento"].value_counts().reset_index()
                conteo.columns = ["medicamento", "count"]
                fig = px.bar(conteo, x="medicamento", y="count",
                            color="medicamento",
                            color_discrete_sequence=["#c9a84c", "#f0c96e", "#1a3a6e",
                                                    "#4fc3f7", "#e63946"])
                fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                font=dict(color="white"), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        if not eeg_lista:
            st.info("Sin analisis EEG aun.")
        else:
            df = pd.DataFrame(eeg_lista)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Estados EEG")
                if "estado" in df.columns:
                    colores_eeg = {
                        "normal": "#40916c",
                        "anormal": "#f4a261",
                        "critico": "#e63946"
                    }
                    conteo = df["estado"].value_counts().reset_index()
                    conteo.columns = ["estado", "count"]
                    fig = px.pie(conteo, names="estado", values="count",
                                color="estado", color_discrete_map=colores_eeg)
                    fig.update_layout(plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                                    font=dict(color="white"))
                    st.plotly_chart(fig,)
