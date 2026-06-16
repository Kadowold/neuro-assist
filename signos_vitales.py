import streamlit as st
import datetime

def semaforo(valor, min_normal, max_normal, min_alerta, max_alerta, unidad=""):
    if valor < min_alerta or valor > max_alerta:
        return "🔴", "CRITICO", "error"
    elif valor < min_normal or valor > max_normal:
        return "🟡", "ALERTA", "warning"
    else:
        return "🟢", "NORMAL", "success"

def signos_vitales(db):
    st.header("Calculadora de Signos Vitales")
    st.markdown("> Evalua signos vitales segun edad con semaforo visual en tiempo real.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="sv_paciente")

    st.subheader("Edad del paciente")
    col1, col2 = st.columns(2)
    with col1:
        unidad_edad = st.radio("Unidad", ["Meses", "Anos"], horizontal=True)
    with col2:
        if unidad_edad == "Meses":
            edad = st.number_input("Edad (meses)", min_value=0, max_value=216, value=12)
            edad_meses = edad
        else:
            edad = st.number_input("Edad (anos)", min_value=0, max_value=18, value=5)
            edad_meses = edad * 12

    # Rangos normales por edad en meses
    # (FC_min, FC_max, FC_alerta_min, FC_alerta_max,
    #  FR_min, FR_max, FR_alerta_min, FR_alerta_max,
    #  PAS_min, PAS_max, PAS_alerta_min, PAS_alerta_max)
    def rangos_por_edad(meses):
        if meses < 1:
            return (100,160,80,180, 40,60,30,70, 60,90,50,100)
        elif meses < 3:
            return (100,150,80,180, 35,55,25,65, 65,95,55,105)
        elif meses < 6:
            return (90,150,70,175, 30,50,20,60, 70,100,60,110)
        elif meses < 12:
            return (80,140,60,165, 25,45,20,55, 72,104,62,114)
        elif meses < 24:
            return (75,135,55,160, 20,40,15,50, 74,106,64,116)
        elif meses < 60:
            return (70,125,50,150, 20,35,15,45, 78,110,68,120)
        elif meses < 108:
            return (65,115,45,140, 18,30,12,40, 80,114,70,124)
        else:
            return (55,105,40,130, 15,25,10,35, 85,120,75,130)

    fc_min, fc_max, fc_amin, fc_amax, fr_min, fr_max, fr_amin, fr_amax, pas_min, pas_max, pas_amin, pas_amax = rangos_por_edad(edad_meses)

    st.divider()
    st.subheader("Ingresa los signos vitales")

    col1, col2 = st.columns(2)
    with col1:
        fc = st.number_input("Frecuencia cardiaca (lpm)", min_value=0, max_value=300, value=100)
        fr = st.number_input("Frecuencia respiratoria (rpm)", min_value=0, max_value=100, value=25)
        temp = st.number_input("Temperatura (C)", min_value=34.0, max_value=42.0, value=37.0, step=0.1)
    with col2:
        pas = st.number_input("Presion arterial sistolica (mmHg)", min_value=0, max_value=250, value=90)
        pad = st.number_input("Presion arterial diastolica (mmHg)", min_value=0, max_value=150, value=60)
        sato2 = st.slider("Saturacion de O2 (%)", 70, 100, 98)

    peso = st.number_input("Peso (kg) - opcional para presion arterial", min_value=0.0, max_value=150.0, value=0.0, step=0.1)

    if st.button("Evaluar signos vitales"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            st.divider()
            st.subheader("Resultado del semaforo")

            # FC
            icon_fc, estado_fc, tipo_fc = semaforo(fc, fc_min, fc_max, fc_amin, fc_amax)
            # FR
            icon_fr, estado_fr, tipo_fr = semaforo(fr, fr_min, fr_max, fr_amin, fr_amax)
            # Temperatura
            icon_t, estado_t, tipo_t = semaforo(temp, 36.0, 37.5, 35.5, 39.0)
            # PAS
            icon_pas, estado_pas, tipo_pas = semaforo(pas, pas_min, pas_max, pas_amin, pas_amax)
            # SatO2
            icon_sat, estado_sat, tipo_sat = semaforo(sato2, 95, 100, 90, 100)

            # Mostrar tarjetas
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"### {icon_fc} Frecuencia Cardiaca")
                st.markdown(f"**{fc} lpm** — {estado_fc}")
                st.caption(f"Normal: {fc_min}-{fc_max} lpm")
                if tipo_fc == "error":
                    st.error("Fuera de rango critico")
                elif tipo_fc == "warning":
                    st.warning("Fuera de rango normal")
                else:
                    st.success("Dentro de rango normal")

            with col2:
                st.markdown(f"### {icon_fr} Frecuencia Respiratoria")
                st.markdown(f"**{fr} rpm** — {estado_fr}")
                st.caption(f"Normal: {fr_min}-{fr_max} rpm")
                if tipo_fr == "error":
                    st.error("Fuera de rango critico")
                elif tipo_fr == "warning":
                    st.warning("Fuera de rango normal")
                else:
                    st.success("Dentro de rango normal")

            with col3:
                st.markdown(f"### {icon_t} Temperatura")
                st.markdown(f"**{temp} C** — {estado_t}")
                st.caption("Normal: 36.0-37.5 C")
                if temp >= 38.0 and edad_meses < 3:
                    st.error("ALERTA: Fiebre en menor de 3 meses — Urgencia")
                elif tipo_t == "error":
                    st.error("Fuera de rango critico")
                elif tipo_t == "warning":
                    st.warning("Fuera de rango normal")
                else:
                    st.success("Dentro de rango normal")

            col4, col5, col6 = st.columns(3)

            with col4:
                st.markdown(f"### {icon_pas} Presion Arterial")
                st.markdown(f"**{pas}/{pad} mmHg** — {estado_pas}")
                st.caption(f"Normal sistolica: {pas_min}-{pas_max} mmHg")
                if tipo_pas == "error":
                    st.error("Fuera de rango critico")
                elif tipo_pas == "warning":
                    st.warning("Fuera de rango normal")
                else:
                    st.success("Dentro de rango normal")

            with col5:
                st.markdown(f"### {icon_sat} Saturacion O2")
                st.markdown(f"**{sato2}%** — {estado_sat}")
                st.caption("Normal: 95-100%")
                if tipo_sat == "error":
                    st.error("Saturacion critica")
                elif tipo_sat == "warning":
                    st.warning("Saturacion baja")
                else:
                    st.success("Saturacion normal")

            with col6:
                st.markdown("### 📊 Resumen")
                estados = [tipo_fc, tipo_fr, tipo_t, tipo_pas, tipo_sat]
                if "error" in estados:
                    st.error("PACIENTE CRITICO\nAtencion inmediata")
                elif "warning" in estados:
                    st.warning("PACIENTE INESTABLE\nMonitoreo continuo")
                else:
                    st.success("PACIENTE ESTABLE\nSignos normales")

            st.divider()
            st.subheader("Rangos normales para esta edad")
            st.markdown(f"""
            | Signo vital | Rango normal | Rango alerta |
            |---|---|---|
            | Frecuencia cardiaca | {fc_min}-{fc_max} lpm | <{fc_amin} o >{fc_amax} lpm |
            | Frecuencia respiratoria | {fr_min}-{fr_max} rpm | <{fr_amin} o >{fr_amax} rpm |
            | Temperatura | 36.0-37.5 C | <35.5 o >39.0 C |
            | Presion sistolica | {pas_min}-{pas_max} mmHg | <{pas_amin} o >{pas_amax} mmHg |
            | Saturacion O2 | 95-100% | <90% |
            """)

            try:
                db.collection("signos_vitales").add({
                    "paciente": paciente,
                    "edad_meses": int(edad_meses),
                    "fc": int(fc),
                    "fr": int(fr),
                    "temperatura": float(temp),
                    "pas": int(pas),
                    "pad": int(pad),
                    "sato2": int(sato2),
                    "estado_fc": estado_fc,
                    "estado_fr": estado_fr,
                    "estado_temp": estado_t,
                    "estado_pas": estado_pas,
                    "estado_sat": estado_sat,
                    "fecha": datetime.datetime.now()
                })
                st.success("Evaluacion guardada en Firebase.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
