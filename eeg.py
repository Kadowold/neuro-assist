import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

def analizar_eeg_con_ia(señal, fs):
    from scipy import signal as scipy_signal
    
    resultados = []
    alertas = []
    
    # Calcular potencia en bandas de frecuencia
    freqs, psd = scipy_signal.welch(señal, fs, nperseg=min(256, len(señal)))
    
    def potencia_banda(f_min, f_max):
        idx = np.where((freqs >= f_min) & (freqs <= f_max))
        return np.trapz(psd[idx], freqs[idx])
    
    delta = potencia_banda(0.5, 4)
    theta = potencia_banda(4, 8)
    alpha = potencia_banda(8, 13)
    beta = potencia_banda(13, 30)
    gamma = potencia_banda(30, 50)
    total = delta + theta + alpha + beta + gamma
    
    # Porcentajes
    p_delta = (delta / total) * 100
    p_theta = (theta / total) * 100
    p_alpha = (alpha / total) * 100
    p_beta = (beta / total) * 100
    p_gamma = (gamma / total) * 100
    
    # Deteccion de patrones
    if p_delta > 50:
        alertas.append("ALERTA: Actividad delta elevada (>50%) — Puede indicar encefalopatia o sueno profundo")
    if p_theta > 35:
        alertas.append("ALERTA: Actividad theta elevada — Posible disfuncion cognitiva o somnolencia")
    if p_alpha < 10:
        alertas.append("AVISO: Actividad alpha reducida — Posible estado de alerta o ansiedad")
    if p_beta > 40:
        alertas.append("AVISO: Actividad beta elevada — Posible efecto de benzodiazepinas o ansiedad")
    if p_gamma > 20:
        alertas.append("ALERTA: Actividad gamma elevada — Posible actividad epileptiforme")
    
    # Deteccion de picos anormales (posibles espigas epilepticas)
    umbral = np.mean(señal) + 3.5 * np.std(señal)
    picos = np.where(np.abs(señal) > umbral)[0]
    if len(picos) > 5:
        alertas.append(f"ALERTA CRITICA: {len(picos)} picos de alta amplitud detectados — Posible actividad epileptiforme")
    
    # Interpretacion general
    if not alertas:
        interpretacion = "EEG dentro de parametros normales"
        estado = "normal"
    elif any("CRITICA" in a for a in alertas):
        interpretacion = "Patron anormal critico detectado — Evaluacion neurologica urgente"
        estado = "critico"
    else:
        interpretacion = "Patron anormal detectado — Se recomienda evaluacion neurologica"
        estado = "anormal"
    
    return {
        "bandas": {
            "Delta (0.5-4 Hz)": round(p_delta, 1),
            "Theta (4-8 Hz)": round(p_theta, 1),
            "Alpha (8-13 Hz)": round(p_alpha, 1),
            "Beta (13-30 Hz)": round(p_beta, 1),
            "Gamma (30-50 Hz)": round(p_gamma, 1),
        },
        "alertas": alertas,
        "interpretacion": interpretacion,
        "estado": estado,
        "picos_detectados": len(picos)
    }


def graficar_señal(tiempo, señal, titulo="Señal EEG", alertas=[]):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tiempo,
        y=señal,
        mode="lines",
        name="EEG",
        line=dict(color="#4fc3f7", width=1)
    ))
    
    # Marcar picos anormales
    umbral = np.mean(señal) + 3.5 * np.std(señal)
    picos = np.where(np.abs(señal) > umbral)[0]
    if len(picos) > 0:
        fig.add_trace(go.Scatter(
            x=tiempo[picos],
            y=señal[picos],
            mode="markers",
            name="Picos anormales",
            marker=dict(color="#e63946", size=8, symbol="x")
        ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Tiempo (s)",
        yaxis_title="Amplitud (uV)",
        plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117",
        font=dict(color="white"),
        height=300,
        showlegend=True,
        legend=dict(bgcolor="#1a1f2e")
    )
    return fig


def graficar_bandas(bandas):
    nombres = list(bandas.keys())
    valores = list(bandas.values())
    colores = ["#4fc3f7", "#81d4fa", "#a5d6a7", "#ffb74d", "#e63946"]
    
    fig = go.Figure(go.Bar(
        x=nombres,
        y=valores,
        marker_color=colores,
        text=[f"{v}%" for v in valores],
        textposition="outside"
    ))
    fig.update_layout(
        title="Distribucion de bandas de frecuencia",
        yaxis_title="Potencia (%)",
        plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117",
        font=dict(color="white"),
        height=350,
        yaxis=dict(range=[0, 100])
    )
    return fig


def generar_eeg_demo(tipo="normal"):
    fs = 256
    duracion = 10
    t = np.linspace(0, duracion, fs * duracion)
    
    if tipo == "normal":
        # EEG normal: predominio alpha y beta
        señal = (
            2.0 * np.sin(2 * np.pi * 10 * t) +   # Alpha
            1.0 * np.sin(2 * np.pi * 20 * t) +   # Beta
            0.5 * np.sin(2 * np.pi * 2 * t) +    # Delta leve
            0.3 * np.random.randn(len(t))          # Ruido
        )
    elif tipo == "epileptico":
        # EEG con actividad epileptiforme: espigas
        señal = (
            1.5 * np.sin(2 * np.pi * 3 * t) +
            0.5 * np.sin(2 * np.pi * 8 * t) +
            0.3 * np.random.randn(len(t))
        )
        # Agregar espigas epilepticas
        for i in range(0, len(t), fs * 2):
            if i + 10 < len(t):
                señal[i:i+10] += np.array([0, 5, 15, 25, 20, 10, -5, -15, -10, -5])
    elif tipo == "encefalopatia":
        # EEG con encefalopatia: predominio delta
        señal = (
            8.0 * np.sin(2 * np.pi * 1.5 * t) +
            4.0 * np.sin(2 * np.pi * 3 * t) +
            1.0 * np.sin(2 * np.pi * 6 * t) +
            0.5 * np.random.randn(len(t))
        )
    
    return t, señal, fs


def visualizador_eeg(db):
    st.header("Visualizador de EEG con IA")
    st.markdown("> Analiza señales electroencefalograficas y detecta patrones anormales.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="eeg_paciente")

    modo = st.radio("Modo de analisis", [
        "Demo simulada",
        "Subir archivo EEG (.edf)"
    ], horizontal=True)

    if modo == "Demo simulada":
        st.subheader("Selecciona el tipo de señal")
        tipo_demo = st.selectbox("Tipo de EEG simulado", [
            "normal",
            "epileptico",
            "encefalopatia"
        ])
        
        descripciones = {
            "normal": "EEG con predominio de ondas alpha y beta. Patron tipico de paciente despierto y relajado.",
            "epileptico": "EEG con espigas epileptiformes periodicas. Simula actividad ictal.",
            "encefalopatia": "EEG con predominio de ondas delta. Patron tipico de encefalopatia metabolica."
        }
        st.info(descripciones[tipo_demo])
        
        if st.button("Analizar EEG"):
            if paciente == "":
                st.warning("Por favor ingresa el nombre del paciente.")
            else:
                with st.spinner("Analizando señal EEG con IA..."):
                    t, señal, fs = generar_eeg_demo(tipo_demo)
                    mostrar_resultados(t, señal, fs, paciente, db, tipo_demo)

    else:
        st.subheader("Sube tu archivo EEG")
        st.info("Formato soportado: .edf (European Data Format)")
        archivo = st.file_uploader("Selecciona archivo .edf", type=["edf"])
        
        if archivo and st.button("Analizar EEG"):
            if paciente == "":
                st.warning("Por favor ingresa el nombre del paciente.")
            else:
                with st.spinner("Leyendo y analizando archivo EEG..."):
                    try:
                        import mne
                        import tempfile, os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as tmp:
                            tmp.write(archivo.read())
                            tmp_path = tmp.name
                        
                        raw = mne.io.read_raw_edf(tmp_path, preload=True, verbose=False)
                        os.unlink(tmp_path)
                        
                        fs = int(raw.info["sfreq"])
                        datos = raw.get_data()
                        canal = datos[0]
                        t = np.linspace(0, len(canal)/fs, len(canal))
                        
                        # Usar solo los primeros 30 segundos
                        max_samples = fs * 30
                        if len(canal) > max_samples:
                            canal = canal[:max_samples]
                            t = t[:max_samples]
                        
                        # Convertir a microvoltios
                        señal = canal * 1e6
                        
                        st.success(f"Archivo cargado: {raw.info['nchan']} canales, {fs} Hz, {len(raw.times)/fs:.1f} segundos")
                        mostrar_resultados(t, señal, fs, paciente, db, "archivo_real")
                        
                    except Exception as e:
                        st.error(f"Error al leer el archivo: {e}")
                        st.info("Asegurate de que el archivo sea un EDF valido.")


def mostrar_resultados(t, señal, fs, paciente, db, fuente):
    resultado = analizar_eeg_con_ia(señal, fs)
    
    st.divider()
    st.subheader("Señal EEG")
    fig_señal = graficar_señal(t, señal, f"EEG - {paciente}")
    st.plotly_chart(fig_señal, use_container_width=True)
    
    st.subheader("Analisis de frecuencias")
    fig_bandas = graficar_bandas(resultado["bandas"])
    st.plotly_chart(fig_bandas, use_container_width=True)
    
    st.subheader("Resultado del analisis IA")
    col1, col2, col3 = st.columns(3)
    col1.metric("Delta", f"{resultado['bandas']['Delta (0.5-4 Hz)']}%")
    col2.metric("Alpha", f"{resultado['bandas']['Alpha (8-13 Hz)']}%")
    col3.metric("Beta", f"{resultado['bandas']['Beta (13-30 Hz)']}%")
    
    st.divider()
    if resultado["alertas"]:
        for alerta in resultado["alertas"]:
            if "CRITICA" in alerta:
                st.error(f"🚨 {alerta}")
            elif "ALERTA" in alerta:
                st.warning(f"⚠️ {alerta}")
            else:
                st.info(f"ℹ️ {alerta}")
    
    if resultado["estado"] == "normal":
        st.success(f"Interpretacion IA: {resultado['interpretacion']}")
    elif resultado["estado"] == "critico":
        st.error(f"Interpretacion IA: {resultado['interpretacion']}")
    else:
        st.warning(f"Interpretacion IA: {resultado['interpretacion']}")
    
    st.caption("Este analisis es una herramienta de apoyo. No reemplaza el criterio del especialista.")
    
    try:
        db.collection("eeg").add({
            "paciente": paciente,
            "fuente": fuente,
            "interpretacion": resultado["interpretacion"],
            "estado": resultado["estado"],
            "picos_detectados": resultado["picos_detectados"],
            "bandas": resultado["bandas"],
            "alertas": resultado["alertas"],
            "fecha": datetime.datetime.now()
        })
        st.success("Analisis guardado en Firebase.")
    except Exception as e:
        st.error(f"Error al guardar: {e}")
