import streamlit as st
import pandas as pd
import plotly.express as px
import io
import datetime
from datetime import date
from styles import aplicar_estilos

# ----------------- IMPORTANTE: INTEGRACIÓN DE FIREBASE -----------------
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase (Usa los secretos guardados de forma segura)
if not firebase_admin._apps:
    try:
        firebase_creds = dict(st.secrets["firebase"])
        # Limpieza obligatoria para que los saltos de línea de la clave privada funcionen en la nube
        firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    except KeyError:
        st.error("No se encontraron las credenciales de Firebase en st.secrets. Verifica tu archivo .streamlit/secrets.toml")

# Conexión al cliente de Firestore
db = firestore.client()
# ----------------------------------------------------------------------

# Nota: Si aún usas 'generar_pdf' de tu archivo database, asegúrate de importarlo.
# Si tu archivo 'database' generaba la tabla SQLite local, ya no necesitamos crear_tabla().
from database import generar_pdf 

st.set_page_config(page_title="NeuroApp", page_icon="🧠", layout="centered")
aplicar_estilos() # Aplicamos tus estilos personalizados

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
    tipo_sintoma = st.selectbox("Tipo de sintoma", ["Migrana", "Convulsion", "Mareo", "Perdida de memoria", "Hormigueo", "Visión borrosa", "Otro"])
    intensidad = st.slider("Intensidad del dolor (1=leve, 10=grave)", 1, 10, 5)
    duracion = st.number_input("Duracion (en minutos)", min_value=1, value=30)
    desencadenante = st.selectbox("Posible desencadenante", ["Estres", "Falta de sueño", "Alimentación", "Pantallas", "Clima", "Sin desencadenante aparente", "Otro"])
    notas = st.text_area("Notas adicionales (opcional)")

    if st.button("Guardar sintoma"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            # --- GUARDAR EN FIREBASE FIRESTORE ---
            # Pasamos la fecha de tipo date a datetime para que Firebase la guarde correctamente con zona horaria
            fecha_convertida = datetime.datetime.combine(fecha, datetime.time.min)
            
            # Estructuramos el documento en un diccionario de Python
            datos_sintoma = {
                "paciente": paciente, # Guardamos el nombre para poder buscarlo en el historial
                "fecha": fecha_convertida,
                "tipo_sintoma": tipo_sintoma,
                "intensidad": intensidad,
                "duración": duracion,
                "desencadenante": desencadenante,
                "notas": notas,
                "creado_el": firestore.SERVER_TIMESTAMP # Registra el momento exacto de guardado
            }
            
            try:
                # Guardamos en la colección 'sintomas' de Firebase
                db.collection("sintomas").add(datos_sintoma)
                st.success("Sintoma guardado correctamente en la nube (Firebase).")
            except Exception as e:
                st.error(f"Error al conectar con la base de datos: {e}")

elif menu == "Ver historial":
    st.header("Historial de sintomas")
    paciente_buscar = st.text_input("Buscar paciente por nombre")

    if paciente_buscar:
        # --- CONSULTAR EN FIREBASE FIRESTORE ---
        try:
            # Traemos los documentos de la colección 'sintomas' donde el paciente coincida exactamente
            # Nota: Firestore requiere búsquedas exactas, puedes pasarlo a minúsculas o mayúsculas uniformes si lo prefieres
            query = db.collection("sintomas").where("paciente", "==", paciente_buscar).order_by("fecha", direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            # Pasamos los resultados de Firebase a una lista de diccionarios
            lista_registros = []
            for doc in docs:
                datos = doc.to_dict()
                # Convertimos las marcas de tiempo de Firebase a formato de fecha legible de Python
                if "fecha" in datos and datos["fecha"] is not None:
                    datos["fecha"] = datos["fecha"].date()
                lista_registros.append(datos)
                
            # Convertimos la lista de registros a un DataFrame de Pandas para mantener tus gráficas idénticas
            df = pd.DataFrame(lista_registros)

            if df.empty:
                st.info("No se encontraron registros exactos para ese paciente.")
            else:
                st.success(f"Se encontraron {len(df)} registro(s).")
                
                # Seleccionamos y ordenamos las columnas para mostrar en tu tabla de la app
                columnas_mostrar = ["fecha", "tipo_sintoma", "intensidad", "duración", "desencadenante", "notas"]
                df_tabla = df[columnas_mostrar]
                
                st.dataframe(df_tabla, use_container_width=True)
                st.divider()

                # GRAFICA 1: Frecuencia de sintomas
                st.subheader("Frecuencia de sintomas")
                fig1 = px.bar(
                    df_tabla["tipo_sintoma"].value_counts().reset_index(),
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

                # GRAFICA 3: Desencadenantes mas comunes
                st.subheader("Desencadenantes mas frecuentes")
                fig3 = px.pie(
                    df_tabla,
                    names="desencadenante",
                    title="Distribucion de desencadenantes"
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Sección de Botón exportar PDF
                st.divider()
                st.subheader("Exportar reporte")
                if st.button("Descargar reporte PDF"):
                    pdf = generar_pdf(paciente_buscar, df_tabla)
                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        label="Haz click aqui para descargar",
                        data=pdf_bytes,
                        file_name=f"reporte_{paciente_buscar}.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            # Nota para desarrollo: Si te pide crear un "índice compuesto" en la consola de Firebase para usar order_by,
            # la misma terminal de Streamlit te dará un enlace directo para crearlo con un solo clic.
            st.error(f"Error al recuperar los datos: {e}")
            
    else:
        st.info("Escribe el nombre de un paciente para ver su historial.")
