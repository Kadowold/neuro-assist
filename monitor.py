import streamlit as st
import datetime
import pandas as pd

def monitor_criticos(db):
    st.header("Monitor de Pacientes Criticos")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2d0000, #4a0d0d);
        border: 1px solid #e6394644;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #ff6b6b; font-weight: 600; font-size: 15px">
            🚨 Monitor en tiempo real — Alertas criticas
        </div>
        <div style="color: #fca5a5; font-size: 13px; margin-top: 4px">
            Detecta automaticamente pacientes con signos vitales fuera de rango
            o resultados criticos en escalas clinicas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    if st.button("🔄 Actualizar monitor", use_container_width=True):
        st.rerun()

    alertas_criticas = []
    alertas_advertencia = []

    # Revisar signos vitales
    try:
        docs = db.collection("signos_vitales").stream()
        for doc in docs:
            d = doc.to_dict()
            paciente = d.get("paciente", "Desconocido")
            fecha = d.get("fecha", "")
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime("%Y-%m-%d %H:%M")

            criticos = []
            advertencias = []

            if d.get("estado_fc") == "CRITICO":
                criticos.append(f"FC critica: {d.get('fc')} lpm")
            elif d.get("estado_fc") == "ALERTA":
                advertencias.append(f"FC en alerta: {d.get('fc')} lpm")

            if d.get("estado_fr") == "CRITICO":
                criticos.append(f"FR critica: {d.get('fr')} rpm")
            elif d.get("estado_fr") == "ALERTA":
                advertencias.append(f"FR en alerta: {d.get('fr')} rpm")

            if d.get("estado_sat") == "CRITICO":
                criticos.append(f"SatO2 critica: {d.get('sato2')}%")
            elif d.get("estado_sat") == "ALERTA":
                advertencias.append(f"SatO2 baja: {d.get('sato2')}%")

            if d.get("estado_temp") == "CRITICO":
                criticos.append(f"Temperatura critica: {d.get('temperatura')}C")

            if criticos:
                alertas_criticas.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "Signos Vitales",
                    "alertas": criticos
                })
            if advertencias:
                alertas_advertencia.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "Signos Vitales",
                    "alertas": advertencias
                })
    except Exception as e:
        st.error(f"Error al leer signos vitales: {e}")

    # Revisar triaje
    try:
        docs = db.collection("triaje").stream()
        for doc in docs:
            d = doc.to_dict()
            paciente = d.get("paciente", "Desconocido")
            fecha = d.get("fecha", "")
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime("%Y-%m-%d %H:%M")
            nivel = d.get("nivel_triaje", "")
            if "ROJO" in nivel:
                alertas_criticas.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "Triaje",
                    "alertas": [f"Triaje ROJO — Emergencia: {nivel}"]
                })
            elif "NARANJA" in nivel:
                alertas_advertencia.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "Triaje",
                    "alertas": [f"Triaje NARANJA — Urgencia: {nivel}"]
                })
    except:
        pass

    # Revisar EEG criticos
    try:
        docs = db.collection("eeg").stream()
        for doc in docs:
            d = doc.to_dict()
            paciente = d.get("paciente", "Desconocido")
            fecha = d.get("fecha", "")
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime("%Y-%m-%d %H:%M")
            if d.get("estado") == "critico":
                alertas_criticas.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "EEG",
                    "alertas": [f"EEG CRITICO: {d.get('interpretacion', '')}"]
                })
            elif d.get("estado") == "anormal":
                alertas_advertencia.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": "EEG",
                    "alertas": [f"EEG anormal: {d.get('interpretacion', '')}"]
                })
    except:
        pass

    # Revisar calculadoras criticas
    try:
        docs = db.collection("calculadoras").stream()
        for doc in docs:
            d = doc.to_dict()
            paciente = d.get("paciente", "Desconocido")
            fecha = d.get("fecha", "")
            if hasattr(fecha, 'strftime'):
                fecha = fecha.strftime("%Y-%m-%d %H:%M")
            escala = d.get("escala", "")
            puntaje = d.get("puntaje", 0)
            interpretacion = d.get("interpretacion", "")

            critico = False
            if escala == "Glasgow" and isinstance(puntaje, (int, float)) and puntaje < 9:
                critico = True
            elif escala == "NIHSS" and isinstance(puntaje, (int, float)) and puntaje > 15:
                critico = True
            elif escala == "MMSE" and isinstance(puntaje, (int, float)) and puntaje < 11:
                critico = True

            if critico:
                alertas_criticas.append({
                    "paciente": paciente,
                    "fecha": fecha,
                    "modulo": f"Escala {escala}",
                    "alertas": [f"Puntaje critico {escala}: {puntaje} — {interpretacion}"]
                })
    except:
        pass

    # Mostrar resultados
    col1, col2, col3 = st.columns(3)
    col1.metric("Alertas criticas", len(alertas_criticas),
                delta=None if len(alertas_criticas) == 0 else f"{len(alertas_criticas)} urgentes")
    col2.metric("Advertencias", len(alertas_advertencia))
    col3.metric("Total monitoreado", len(alertas_criticas) + len(alertas_advertencia))

    st.divider()

    if not alertas_criticas and not alertas_advertencia:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0d4a2e, #1b5e3b);
            border: 1px solid #40916c66;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
        ">
            <div style="font-size: 48px">✅</div>
            <div style="color: #a7f3d0; font-size: 18px; font-weight: 600; margin-top: 8px">
                Sin alertas activas
            </div>
            <div style="color: #6ee7b7; font-size: 13px; margin-top: 4px">
                Todos los pacientes monitoreados estan dentro de parametros normales
            </div>
        </div>
        """, unsafe_allow_html=True)

    if alertas_criticas:
        st.subheader("🚨 Alertas criticas")
        for alerta in alertas_criticas:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2d0000, #4a0d0d);
                border: 2px solid #e63946;
                border-radius: 12px;
                padding: 16px 20px;
                margin: 8px 0;
                box-shadow: 0 4px 20px #e6394644;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center">
                    <span style="color: #ff6b6b; font-weight: 700; font-size: 16px">
                        🚨 {alerta['paciente']}
                    </span>
                    <span style="
                        background: #e63946;
                        color: white;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 11px;
                        font-weight: 600;
                    ">CRITICO</span>
                </div>
                <div style="color: #fca5a5; font-size: 12px; margin-top: 4px">
                    📅 {alerta['fecha']} — 🏥 {alerta['modulo']}
                </div>
                <div style="margin-top: 8px">
                    {"".join([f'<div style="color: #fecaca; font-size: 13px; margin-top: 4px">⚠️ {a}</div>' for a in alerta['alertas']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if alertas_advertencia:
        st.subheader("⚠️ Advertencias")
        for alerta in alertas_advertencia:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2d1a00, #4a2e00);
                border: 1px solid #f4a261;
                border-radius: 12px;
                padding: 16px 20px;
                margin: 8px 0;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center">
                    <span style="color: #fb923c; font-weight: 700; font-size: 15px">
                        ⚠️ {alerta['paciente']}
                    </span>
                    <span style="
                        background: #f4a261;
                        color: #0a1628;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 11px;
                        font-weight: 600;
                    ">ALERTA</span>
                </div>
                <div style="color: #fdba74; font-size: 12px; margin-top: 4px">
                    📅 {alerta['fecha']} — 🏥 {alerta['modulo']}
                </div>
                <div style="margin-top: 8px">
                    {"".join([f'<div style="color: #fed7aa; font-size: 13px; margin-top: 4px">• {a}</div>' for a in alerta['alertas']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
