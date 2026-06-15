import streamlit as st
import pandas as pd
import plotly.express as px
import io
from database import crear_tabla, crear_conexion, generar_pdf
from datetime import date
from database import crear_tabla, crear_conexion
from styles import aplicar_estilos

crear_tabla()

st.set_page_config(page_title="NeuroApp", page_icon="🧠", layout="centered")
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("## 🧠")
with col2:
    st.markdown("# NeuroApp")
    st.markdown("*Sistema de seguimiento de sintomas neurologicos*")
st.divider()

menu = st.sidebar.selectbox("Navegacion", ["Registrar sintoma", "Ver historial"])

if menu == "Registrar sintoma":
    st.header("Registrar nuevo sintoma")
    paciente = st.text_input("Nombre del paciente")
    fecha = st.date_input("Fecha del sintoma", value=date.today())
    tipo_sintoma = st.selectbox("Tipo de sintoma", ["Migrana", "Convulsion", "Mareo", "Perdida de memoria", "Hormigueo", "Vision borrosa", "Otro"])
    intensidad = st.slider("Intensidad del dolor (1=leve, 10=severo)", 1, 10, 5)
    duracion = st.number_input("Duracion (en minutos)", min_value=1, value=30)
    desencadenante = st.selectbox("Posible desencadenante", ["Estres", "Falta de sueno", "Alimentacion", "Pantallas", "Clima", "Sin desencadenante aparente", "Otro"])
    notas = st.text_area("Notas adicionales (opcional)")

    if st.button("Guardar sintoma"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            conexion = crear_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO sintomas (paciente, fecha, tipo_sintoma, intensidad, duracion, desencadenante, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (paciente, str(fecha), tipo_sintoma, intensidad, duracion, desencadenante, notas))
            conexion.commit()
            conexion.close()
            st.success("Sintoma guardado correctamente.")

elif menu == "Ver historial":
    st.header("Historial de sintomas")
    paciente_buscar = st.text_input("Buscar paciente por nombre")

    if paciente_buscar:
        conexion = crear_conexion()
        df = pd.read_sql_query("""
            SELECT fecha, tipo_sintoma, intensidad, duracion, desencadenante, notas
            FROM sintomas WHERE paciente LIKE ?
            ORDER BY fecha DESC
        """, conexion, params=(f"%{paciente_buscar}%",))
        conexion.close()

        if df.empty:
            st.info("No se encontraron registros para ese paciente.")
        else:
            st.success(f"Se encontraron {len(df)} registro(s).")
            st.dataframe(df, use_container_width=True)
            st.divider()

            # GRAFICA 1: Frecuencia de sintomas
            st.subheader("Frecuencia de sintomas")
            fig1 = px.bar(
                df["tipo_sintoma"].value_counts().reset_index(),
                x="tipo_sintoma",
                y="count",
                labels={"tipo_sintoma": "Tipo de sintoma", "count": "Veces registrado"},
                color="tipo_sintoma"
            )
            st.plotly_chart(fig1, use_container_width=True)

            # GRAFICA 2: Intensidad en el tiempo
            st.subheader("Intensidad a lo largo del tiempo")
            df_sorted = df.sort_values("fecha")
            fig2 = px.line(
                df_sorted,
                x="fecha",
                y="intensidad",
                markers=True,
                labels={"fecha": "Fecha", "intensidad": "Intensidad (1-10)"},
                color_discrete_sequence=["#e63946"]
            )
            st.plotly_chart(fig2, use_container_width=True)

            # GRAFICA 3: Desencadenantes mas comunes
            st.subheader("Desencadenantes mas frecuentes")
            fig3 = px.pie(
                df,
                names="desencadenante",
                title="Distribucion de desencadenantes"
            )
            st.plotly_chart(fig3, use_container_width=True)
            

    else:
        st.info("Escribe el nombre de un paciente para ver su historial.")
        # Boton exportar PDF
st.divider()
st.subheader("Exportar reporte")
if st.button("Descargar reporte PDF"):
    pdf = generar_pdf(paciente_buscar, df)
    pdf_bytes = bytes(pdf.output())
    st.download_button(
        label="Haz click aqui para descargar",
        data=pdf_bytes,
        file_name=f"reporte_{paciente_buscar}.pdf",
        mime="application/pdf"
    )