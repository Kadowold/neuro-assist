import streamlit as st
import datetime
import pandas as pd

def agenda_medica(db):
    st.header("Agenda Medica")
    st.markdown("> Gestiona citas y seguimientos de tus pacientes.")
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📅 Nueva cita",
        "📋 Ver agenda",
        "🔔 Proximas citas"
    ])

    with tab1:
        st.subheader("Agendar nueva cita")

        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del paciente", key="agenda_paciente")
            fecha = st.date_input("Fecha de la cita", value=datetime.date.today())
            hora = st.time_input("Hora de la cita", value=datetime.time(9, 0))
        with col2:
            tipo_cita = st.selectbox("Tipo de cita", [
                "Consulta general",
                "Consulta neurologica",
                "Control pediatrico",
                "Seguimiento",
                "Urgencia",
                "Primera vez",
                "Resultado de estudios",
                "Vacunacion"
            ])
            prioridad = st.selectbox("Prioridad", [
                "Normal",
                "Alta",
                "Urgente"
            ])

        motivo = st.text_area("Motivo de la cita", placeholder="Describe brevemente el motivo...")
        notas = st.text_area("Notas adicionales (opcional)")

        if st.button("Guardar cita"):
            if paciente == "":
                st.warning("Por favor ingresa el nombre del paciente.")
            else:
                fecha_hora = datetime.datetime.combine(fecha, hora)
                try:
                    db.collection("agenda").add({
                        "paciente": paciente,
                        "fecha": fecha_hora,
                        "fecha_solo": str(fecha),
                        "hora": str(hora),
                        "tipo_cita": tipo_cita,
                        "prioridad": prioridad,
                        "motivo": motivo,
                        "notas": notas,
                        "estado": "Pendiente",
                        "creado_por": st.session_state.get("usuario", ""),
                        "creado_el": datetime.datetime.now()
                    })
                    st.success(f"Cita agendada para {paciente} el {fecha} a las {hora}")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    with tab2:
        st.subheader("Ver agenda por fecha")

        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde", value=datetime.date.today())
        with col2:
            fecha_fin = st.date_input("Hasta", value=datetime.date.today() + datetime.timedelta(days=7))

        if st.button("Buscar citas"):
            try:
                docs = db.collection("agenda").stream()
                citas = []
                for doc in docs:
                    datos = doc.to_dict()
                    datos["id"] = doc.id
                    if "fecha_solo" in datos:
                        fecha_cita = datetime.date.fromisoformat(datos["fecha_solo"])
                        if fecha_inicio <= fecha_cita <= fecha_fin:
                            citas.append(datos)

                if not citas:
                    st.info("No hay citas en ese rango de fechas.")
                else:
                    st.success(f"Se encontraron {len(citas)} cita(s).")

                    for cita in sorted(citas, key=lambda x: x.get("fecha_solo", "")):
                        prioridad = cita.get("prioridad", "Normal")
                        color = "#e63946" if prioridad == "Urgente" else "#f4a261" if prioridad == "Alta" else "#4fc3f7"
                        estado = cita.get("estado", "Pendiente")
                        icon_estado = "✅" if estado == "Completada" else "⏳" if estado == "Pendiente" else "❌"

                        st.markdown(f"""
                        <div style="
                            background: #1a1f2e;
                            border-left: 4px solid {color};
                            border-radius: 10px;
                            padding: 16px;
                            margin: 8px 0;
                        ">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: white; font-weight: 700; font-size: 16px">
                                    👤 {cita.get('paciente', '')}
                                </span>
                                <span style="color: {color}; font-weight: 600">
                                    {prioridad}
                                </span>
                            </div>
                            <div style="color: #90caf9; margin-top: 4px">
                                📅 {cita.get('fecha_solo', '')} — 🕐 {cita.get('hora', '')}
                            </div>
                            <div style="color: #cbd5e1; margin-top: 4px">
                                🏥 {cita.get('tipo_cita', '')} — {icon_estado} {estado}
                            </div>
                            <div style="color: #94a3b8; margin-top: 4px; font-size: 13px">
                                {cita.get('motivo', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Marcar completada", key=f"comp_{cita['id']}"):
                                db.collection("agenda").document(cita["id"]).update({"estado": "Completada"})
                                st.rerun()
                        with col2:
                            if st.button("Cancelar cita", key=f"canc_{cita['id']}"):
                                db.collection("agenda").document(cita["id"]).update({"estado": "Cancelada"})
                                st.rerun()
                        with col3:
                            if st.button("Eliminar", key=f"elim_{cita['id']}"):
                                db.collection("agenda").document(cita["id"]).delete()
                                st.rerun()

            except Exception as e:
                st.error(f"Error al cargar citas: {e}")

    with tab3:
        st.subheader("Proximas citas — Hoy y manana")

        try:
            hoy = datetime.date.today()
            manana = hoy + datetime.timedelta(days=1)

            docs = db.collection("agenda").stream()
            proximas = []
            for doc in docs:
                datos = doc.to_dict()
                datos["id"] = doc.id
                if "fecha_solo" in datos:
                    fecha_cita = datetime.date.fromisoformat(datos["fecha_solo"])
                    if fecha_cita in [hoy, manana]:
                        if datos.get("estado", "Pendiente") == "Pendiente":
                            proximas.append(datos)

            if not proximas:
                st.info("No hay citas pendientes para hoy ni manana.")
            else:
                hoy_citas = [c for c in proximas if c["fecha_solo"] == str(hoy)]
                man_citas = [c for c in proximas if c["fecha_solo"] == str(manana)]

                if hoy_citas:
                    st.markdown("### 📅 Hoy")
                    for cita in sorted(hoy_citas, key=lambda x: x.get("hora", "")):
                        prioridad = cita.get("prioridad", "Normal")
                        color = "#e63946" if prioridad == "Urgente" else "#f4a261" if prioridad == "Alta" else "#40916c"
                        st.markdown(f"""
                        <div style="
                            background: #1a1f2e;
                            border-left: 4px solid {color};
                            border-radius: 10px;
                            padding: 14px;
                            margin: 6px 0;
                        ">
                            <span style="color: white; font-weight: 700">
                                🕐 {cita.get('hora', '')} — {cita.get('paciente', '')}
                            </span>
                            <br>
                            <span style="color: #90caf9; font-size: 13px">
                                {cita.get('tipo_cita', '')} — {prioridad}
                            </span>
                            <br>
                            <span style="color: #94a3b8; font-size: 12px">
                                {cita.get('motivo', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                if man_citas:
                    st.markdown("### 📅 Manana")
                    for cita in sorted(man_citas, key=lambda x: x.get("hora", "")):
                        prioridad = cita.get("prioridad", "Normal")
                        color = "#e63946" if prioridad == "Urgente" else "#f4a261" if prioridad == "Alta" else "#40916c"
                        st.markdown(f"""
                        <div style="
                            background: #1a1f2e;
                            border-left: 4px solid {color};
                            border-radius: 10px;
                            padding: 14px;
                            margin: 6px 0;
                        ">
                            <span style="color: white; font-weight: 700">
                                🕐 {cita.get('hora', '')} — {cita.get('paciente', '')}
                            </span>
                            <br>
                            <span style="color: #90caf9; font-size: 13px">
                                {cita.get('tipo_cita', '')} — {prioridad}
                            </span>
                            <br>
                            <span style="color: #94a3b8; font-size: 12px">
                                {cita.get('motivo', '')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                st.divider()
                st.metric("Total citas pendientes hoy y manana", len(proximas))

        except Exception as e:
            st.error(f"Error al cargar proximas citas: {e}")
