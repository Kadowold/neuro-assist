import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import date
from styles import aplicar_estilos
from database import generar_pdf
from calculadoras import escala_glasgow, escala_nihss, escala_mini_mental, escala_rankin
from pediatria import calculadora_dosis, curvas_crecimiento, desarrollo_infantil, triaje_pediatrico
from login import mostrar_login, mostrar_logout
from eeg import visualizador_eeg
from expediente import expediente_clinico
from chat_ia import chat_medico_ia
from dashboard import dashboard_general
from signos_vitales import signos_vitales
from perfil import mostrar_perfil_sidebar, tutorial_interactivo
from voz_medica import notas_por_voz
from agenda import agenda_medica
from predictor import predictor_riesgo
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
# Control de sesion
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    mostrar_login()
    st.stop()

mostrar_logout()
mostrar_perfil_sidebar()
st.markdown(aplicar_estilos(), unsafe_allow_html=True)
# Boton modo oscuro/claro
if "tema" not in st.session_state:
    st.session_state.tema = "oscuro"

col_tema = st.columns([8, 1])[1]
with col_tema:
    icono = "🌙" if st.session_state.tema == "claro" else "☀️"
    if st.button(icono):
        st.session_state.tema = "claro" if st.session_state.tema == "oscuro" else "oscuro"
        st.rerun()

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #1a3a6e 100%);
    border: 1px solid #c9a84c44;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 #c9a84c22;
    display: flex;
    align-items: center;
    gap: 20px;
">
    <div style="font-size: 52px; filter: drop-shadow(0 0 12px #c9a84c88)">🧠</div>
    <div>
        <div style="
            font-family: 'Playfair Display', serif;
            color: #f0c96e;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            line-height: 1.1;
            text-shadow: 0 2px 20px #c9a84c66;
        ">NeuroApp</div>
        <div style="
            color: #8ba3cc;
            font-size: 0.85rem;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 4px;
        ">Sistema Medico Avanzado</div>
    </div>
    <div style="
        margin-left: auto;
        background: #c9a84c22;
        border: 1px solid #c9a84c44;
        border-radius: 8px;
        padding: 6px 12px;
        color: #c9a84c;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    ">PREMIUM</div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Navegacion", [
    "Dashboard",
    "Agenda medica",
    "Registrar sintoma",
    "Ver historial",
    "Signos vitales",
    "Calculadoras clinicas",
    "Herramientas pediatricas",
    "Visualizador EEG",
    "Notas por voz",
    "Predictor de riesgo IA",
    "Expediente clinico",
    "Chat IA Medica",
    "Tutorial"
])

if menu == "Registrar sintoma":
    st.header("Registrar nuevo sintoma")
    paciente = st.text_input("Nombre del paciente")
    fecha = st.date_input("Fecha del sintoma", value=date.today())
    tipo_sintoma = st.selectbox("Tipo de sintoma", ["Migraña", "Convulsión", "Mareo", "Perdida de memoria", "Hormigueo", "Vision borrosa", "Otro"])
    intensidad = st.slider("Intensidad del dolor (1=leve, 10=grave)", 1, 10, 5)
    duración = st.number_input("Duración (en minutos)", min_value=1, value=30)
    desencadenante = st.selectbox("Posible desencadenante", ["Estrés", "Falta de sueño", "Alimentación", "Pantallas", "Clima", "Sin desencadenante aparente", "Otro"])
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
                "duración": duración,
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
                    datos["duración"] = datos.pop("duración")
                lista_registros.append(datos)
          
            df = pd.DataFrame(lista_registros)

            if df.empty:
                st.info("No se encontraron registros para ese paciente.")
            else:
                st.success(f"Se encontraron {len(df)} registro(s).")

                # Aseguramos que las columnas necesarias existen
                for col in ["tipo_sintoma", "intensidad", "duración", "desencadenante", "notas"]:
                    if col not in df.columns:
                        df[col] = "-"

                columnas_mostrar = ["fecha", "tipo_sintoma", "intensidad", "duración", "desencadenante", "notas"]
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
                    title="Distribucion de desencadenantes",
                    color_discrete_sequence=["#c9a84c", "#f0c96e", "#e07b2a", "#d4a017", "#b8860b", "#f4a261"]
                )
                fig3.update_layout(
                    plot_bgcolor="#c9a84c",
                    paper_bgcolor="#c9a84c",
                    font=dict(color="#0a1628"),
                    title_font=dict(color="#0a1628", size=16),
                    legend=dict(
                        bgcolor="#f0c96e",
                        bordercolor="#0a1628",
                        borderwidth=1,
                        font=dict(color="#0a1628", size=12)
                    )
                )
                fig3.update_traces(
                    textfont=dict(color="#0a1628", size=13),
                    marker=dict(line=dict(color="#0a1628", width=2))
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
elif menu == "Calculadoras clinicas":
    st.sidebar.divider()
    calculadora = st.sidebar.selectbox("Selecciona la escala", [
        "Glasgow",
        "NIHSS (ACV)",
        "Mini-Mental (MMSE)",
        "Rankin Modificada"
    ])

    if calculadora == "Glasgow":
        escala_glasgow()
    elif calculadora == "NIHSS (ACV)":
        escala_nihss()
    elif calculadora == "Mini-Mental (MMSE)":
        escala_mini_mental()
    elif calculadora == "Rankin Modificada":
        escala_rankin()
elif menu == "Herramientas pediatricas":
    st.sidebar.divider()
    herramienta = st.sidebar.selectbox("Selecciona la herramienta", [
        "Calculadora de dosis",
        "Curvas de crecimiento",
        "Desarrollo infantil",
        "Triaje pediatrico"
    ])

    if herramienta == "Calculadora de dosis":
        calculadora_dosis(db)
    elif herramienta == "Curvas de crecimiento":
        curvas_crecimiento(db)
    elif herramienta == "Desarrollo infantil":
        desarrollo_infantil(db)
    elif herramienta == "Triaje pediatrico":
        triaje_pediatrico(db)
elif menu == "Visualizador EEG":
    visualizador_eeg(db)
elif menu == "Expediente clinico":
    expediente_clinico(db)
elif menu == "Chat IA Medica":
    chat_medico_ia(db)
elif menu == "Dashboard":
    dashboard_general(db)
elif menu == "Signos vitales":
    signos_vitales(db)

elif menu == "Tutorial":
    tutorial_interactivo()
elif menu == "Notas por voz":
    notas_por_voz(db)
elif menu == "Agenda medica":
    agenda_medica(db)
elif menu == "Predictor de riesgo IA":
    predictor_riesgo(db)
