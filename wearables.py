import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def interpretar_datos_wearable(fc, spo2, pasos, temperatura, edad_meses):
    alertas = []
    estado_global = "normal"

    if edad_meses < 12:
        fc_min, fc_max = 100, 160
    elif edad_meses < 36:
        fc_min, fc_max = 90, 150
    else:
        fc_min, fc_max = 70, 130

    if fc < fc_min - 20 or fc > fc_max + 20:
        alertas.append(f"FC CRITICA: {fc} lpm (normal {fc_min}-{fc_max})")
        estado_global = "critico"
    elif fc < fc_min or fc > fc_max:
        alertas.append(f"FC fuera de rango: {fc} lpm (normal {fc_min}-{fc_max})")
        if estado_global != "critico":
            estado_global = "alerta"

    if spo2 < 90:
        alertas.append(f"SpO2 CRITICA: {spo2}%")
        estado_global = "critico"
    elif spo2 < 95:
        alertas.append(f"SpO2 baja: {spo2}%")
        if estado_global != "critico":
            estado_global = "alerta"

    if temperatura > 39.5:
        alertas.append(f"Fiebre alta: {temperatura}C")
        if estado_global != "critico":
            estado_global = "alerta"
    elif temperatura >= 38.0 and edad_meses < 3:
        alertas.append(f"URGENTE: Fiebre en menor de 3 meses: {temperatura}C")
        estado_global = "critico"

    return alertas, estado_global


def wearables_monitor(db):
    st.header("Monitor de Wearables")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            ⌚ Integracion con Wearables — Smartwatch y Oximetro
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Registra y monitorea datos de smartwatch y oximetros bluetooth.
            Detecta anomalias en tiempo real con alertas automaticas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📊 Registro manual",
        "📈 Historial y tendencias",
        "🚨 Alertas wearable"
    ])

    with tab1:
        st.subheader("Registrar lectura de wearable")
        st.info("Ingresa los datos del smartwatch u oximetro del paciente manualmente o desde la app del dispositivo.")

        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="wear_paciente")
            edad_meses = st.number_input("Edad (meses)", min_value=0, max_value=216, value=12)
            dispositivo = st.selectbox("Dispositivo", [
                "Oximetro de pulso",
                "Smartwatch pediatrico",
                "Monitor de signos vitales",
                "Pulsioximetro hospitalario",
                "Otro"
            ])
        with col2:
            fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, max_value=300, value=100)
            spo2 = st.slider("SpO2 / Saturacion O2 (%)", 70, 100, 98)
            temperatura = st.number_input("Temperatura (C)", min_value=34.0, max_value=42.0, value=37.0, step=0.1)

        col1, col2 = st.columns(2)
        with col1:
            pasos = st.number_input("Pasos (si aplica)", min_value=0, value=0)
            hrv = st.number_input("Variabilidad FC / HRV (ms, si disponible)", min_value=0, value=0)
        with col2:
            actividad = st.selectbox("Estado del paciente", [
                "En reposo",
                "Dormido",
                "Activo/Jugando",
                "Llorando",
                "Post-convulsion",
                "Otro"
            ])
            notas = st.text_input("Notas adicionales")

        if st.button("Registrar y analizar", use_container_width=True):
            if paciente == "":
                st.warning("Ingresa el nombre del paciente.")
            else:
                alertas, estado = interpretar_datos_wearable(
                    fc, spo2, pasos, temperatura, edad_meses
                )

                try:
                    db.collection("wearables").add({
                        "paciente": paciente,
                        "edad_meses": int(edad_meses),
                        "dispositivo": dispositivo,
                        "fc": int(fc),
                        "spo2": int(spo2),
                        "temperatura": float(temperatura),
                        "pasos": int(pasos),
                        "hrv": int(hrv),
                        "actividad": actividad,
                        "alertas": alertas,
                        "estado": estado,
                        "notas": notas,
                        "medico": st.session_state.get("usuario", ""),
                        "fecha": datetime.datetime.now()
                    })
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                color_fc = "#e63946" if estado == "critico" else "#f4a261" if estado == "alerta" else "#40916c"
                col1.metric("FC", f"{fc} lpm")
                col2.metric("SpO2", f"{spo2}%")
                col3.metric("Temperatura", f"{temperatura}C")
                col4.metric("Estado", estado.upper())

                if alertas:
                    for alerta in alertas:
                        if "CRITICA" in alerta or "URGENTE" in alerta:
                            st.error(f"🚨 {alerta}")
                        else:
                            st.warning(f"⚠️ {alerta}")
                else:
                    st.success("Todos los parametros dentro de rango normal.")

    with tab2:
        st.subheader("Historial y tendencias")
        paciente_hist = st.text_input("Buscar paciente", key="wear_hist")

        if paciente_hist:
            try:
                docs = db.collection("wearables").where(
                    "paciente", "==", paciente_hist
                ).stream()

                registros = []
                for doc in docs:
                    d = doc.to_dict()
                    if "fecha" in d and d["fecha"]:
                        try:
                            d["fecha_str"] = d["fecha"].strftime("%Y-%m-%d %H:%M")
                        except:
                            d["fecha_str"] = str(d["fecha"])
                    registros.append(d)

                if not registros:
                    st.info("Sin registros de wearable para este paciente.")
                else:
                    registros.sort(key=lambda x: x.get("fecha_str", ""))
                    df = pd.DataFrame(registros)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Frecuencia cardiaca**")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df["fecha_str"], y=df["fc"],
                            mode="lines+markers",
                            line=dict(color="#e63946", width=2),
                            name="FC"
                        ))
                        fig.update_layout(
                            plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                            font=dict(color="#e8f0fe"), height=250
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("**Saturacion de oxigeno**")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df["fecha_str"], y=df["spo2"],
                            mode="lines+markers",
                            line=dict(color="#4fc3f7", width=2),
                            name="SpO2"
                        ))
                        fig.add_hline(y=95, line_dash="dash",
                                    line_color="#f4a261",
                                    annotation_text="Limite normal")
                        fig.update_layout(
                            plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                            font=dict(color="#e8f0fe"), height=250,
                            yaxis=dict(range=[85, 101])
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("**Temperatura**")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["fecha_str"], y=df["temperatura"],
                        mode="lines+markers",
                        line=dict(color="#c9a84c", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(201,168,76,0.1)",
                        name="Temperatura"
                    ))
                    fig.add_hline(y=38.0, line_dash="dash",
                                line_color="#f4a261",
                                annotation_text="Umbral fiebre")
                    fig.update_layout(
                        plot_bgcolor="#0a1628", paper_bgcolor="#0d1f3c",
                        font=dict(color="#e8f0fe"), height=250
                    )
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Alertas detectadas por wearables")
        try:
            docs = db.collection("wearables").stream()
            alertas_lista = []
            for doc in docs:
                d = doc.to_dict()
                if d.get("alertas") and d.get("estado") in ["alerta", "critico"]:
                    if "fecha" in d and d["fecha"]:
                        try:
                            d["fecha"] = d["fecha"].strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    alertas_lista.append(d)

            if not alertas_lista:
                st.success("Sin alertas activas de wearables.")
            else:
                st.warning(f"{len(alertas_lista)} alerta(s) detectada(s)")
                for a in alertas_lista:
                    color = "#e63946" if a.get("estado") == "critico" else "#f4a261"
                    st.markdown(f"""
                    <div style="
                        background: #0d1f3c;
                        border-left: 4px solid {color};
                        border-radius: 10px;
                        padding: 14px;
                        margin: 6px 0;
                    ">
                        <div style="color: {color}; font-weight: 700">
                            ⌚ {a.get('paciente')} — {a.get('dispositivo')}
                        </div>
                        <div style="color: #8ba3cc; font-size: 12px">
                            {a.get('fecha')} | FC: {a.get('fc')} | SpO2: {a.get('spo2')}% | Temp: {a.get('temperatura')}C
                        </div>
                        <div style="color: #fca5a5; font-size: 12px; margin-top: 4px">
                            {' | '.join(a.get('alertas', []))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
