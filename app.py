import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import date
from styles import aplicar_estilos
from database import generar_pdf

import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    try:
        firebase_creds = dict(st.secrets["firebase"])
        firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    except KeyError:
        st.error("No se encontraron las credenciales de Firebase.")

db = firestore.client()

st.set_page_config(page_title="NeuroApp", page_icon="🧠", layout="centered")
st.markdown(aplicar_estilos(), unsafe_allow_html=True)

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
    intensidad = st.slider("Intensidad del dolor (1=leve, 10=grave)", 1, 10, 5)
    duracion = st.number_input("Duracion (en minutos)", min_value=1, value=30)
    desencadenante = st.selectbox("Posible desencadenante", ["Estres", "Falta de sueno", "Alimentacion", "Pantallas", "Clima", "Sin desencadenante aparente", "Otro"])
    notas = st.text_area("Notas adicionales (opcional)")

    if st.button("Guardar sintoma"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            fecha_convertida = datetime.datetime.combine(fecha, datetime.time.min)
            datos_sintoma = {
                "paciente": paciente,
                "fecha": fecha_convertida,
                "tipo_sintoma": tipo_sintoma,
                "intensidad": intensidad,
                "duracion": duracion,
                "desencadenante": desencadenante,
                "notas": notas,
                "creado_el": firestore.SERVER_TIMESTAMP
            }
            try:
                db.collection("sintomas").add(datos_sintoma)
                st.success("Sintoma guardado correctamente.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

elif menu == "Ver historial":
    st.header("Historial de sintomas")
    paciente_buscar = st.text_input("Buscar paciente por nombre")

    if paciente_buscar:
        try:
            query = db.collection("sintomas").where(
                "paciente", "==", paciente_buscar
            ).order_by("fecha", direction=firestore.Query.DESCENDING)
            docs = query.stream()

            lista_registros = []
            for doc in docs:
                datos = doc.to_dict()
                # Convertir fecha
                if "fecha" in datos and datos["fecha"] is not None:
                    try:
                        datos["fecha"] = datos["fecha"].date()
                    except:
                        pass
                # Normalizar nombre del campo duracion (con o sin acento)
                if "duración" in datos:
                    datos["duracion"] = datos.pop("duración")
                lista_registros.append(datos)

            df = pd.DataFrame(lista_registros)

            if df.empty:
                st.info("No se encontraron registros para ese paciente.")
            else:
                st.success(f"Se encontraron {len(df)} registro(s).")

                # Aseguramos que las columnas necesarias existen
                for col in ["tipo_sintoma", "intensidad", "duracion", "desencadenante", "notas"]:
                    if col not in df.columns:
                        df[col] = "-"

                columnas_mostrar = ["fecha", "tipo_sintoma", "intensidad", "duracion", "desencadenante", "notas"]
                df_tabla = df[columnas_mostrar].copy()

                st.dataframe(df_tabla, use_container_width=True)
                st.divider()

                # GRAFICA 1: Frecuencia de sintomas
                st.subheader("Frecuencia de sintomas")
                conteo = df_tabla["tipo_sintoma"].value_counts().reset_index()
                conteo.columns = ["tipo_sintoma", "count"]
                fig1 = px.bar(
                    conteo,
                    x="tipo_sintoma",
                    y="count",
                    labels={"tipo_sintoma": "Tipo de sintoma", "count": "Veces registrado"},
                    color="tipo_sintoma"
                )
                st.plotly_chart(fig1, use_container_width=True)

                # GRAFICA 2: Intensidad en el tiempo
                st.subheader("Intensidad a lo largo del tiempo")
                df_sorted = df_tabla.sort_values("fecha")
                fig2 = px.line(
                    df_sorted,
                    x="fecha",
                    y="intensidad",
                    markers=True,
                    labels={"fecha": "Fecha", "intensidad": "Intensidad (1-10)"},
                    color_discrete_sequence=["#e63946"]
                )
                st.plotly_chart(fig2, use_container_width=True)

                # GRAFICA 3: Desencadenantes mas frecuentes
                st.subheader("Desencadenantes mas frecuentes")
                fig3 = px.pie(
                    df_tabla,
                    names="desencadenante",
                    title="Distribucion de desencadenantes"
                )
                st.plotly_chart(fig3, use_container_width=True)

                # Exportar PDF
                st.divider()
                st.subheader("Exportar reporte")
                if st.button("Generar reporte PDF"):
                    pdf = generar_pdf(paciente_buscar, df_tabla)
                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        label="Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"reporte_{paciente_buscar}.pdf",
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"Error al recuperar los datos: {e}")
    else:
        st.info("Escribe el nombre de un paciente para ver su historial.")
