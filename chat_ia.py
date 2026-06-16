import streamlit as st
import anthropic
import datetime

SYSTEM_PROMPT = """Eres MediAssist, un asistente medico especializado de alto nivel integrado en NeuroApp, 
una aplicacion medica profesional. Tienes conocimientos avanzados en:

- Neurologia pediatrica y adultos
- Pediatria general
- Interpretacion de EEG
- Escalas clinicas (Glasgow, NIHSS, MMSE, Rankin)
- Farmacologia pediatrica y neurologica
- Diagnostico diferencial neurologico
- Emergencias neurologicas
- Desarrollo infantil

Tu perfil:
- Respondes SIEMPRE en español
- Eres preciso, claro y profesional
- Das respuestas estructuradas con secciones cuando es necesario
- Incluyes consejos clinicos practicos basados en evidencia
- Alertas sobre situaciones de urgencia o emergencia
- Mencionas cuando algo requiere evaluacion presencial urgente
- Citas guias clinicas actualizadas (OMS, AAP, AAN) cuando es relevante
- Nunca reemplazas la evaluacion clinica presencial pero orientas al medico

Formato de respuestas:
- Usa titulos con ** para secciones importantes
- Lista con - para enumeraciones
- Destaca ALERTAS CRITICAS cuando el caso lo requiera
- Al final siempre incluye un consejo clinico practico

Recuerda: estas hablando con un medico profesional, no con un paciente, 
por lo que puedes usar terminologia medica avanzada."""


def inicializar_chat():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0


def mostrar_mensaje(rol, contenido):
    if rol == "user":
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(contenido)
    else:
        with st.chat_message("assistant", avatar="🧠"):
            st.markdown(contenido)


def obtener_respuesta_ia(mensajes_historial):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Error: No se encontro la API key de Anthropic en los secrets."

        cliente = anthropic.Anthropic(api_key=api_key)

        mensajes_api = [
            {"role": m["rol"], "content": m["contenido"]}
            for m in mensajes_historial
        ]

        respuesta = cliente.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=mensajes_api
        )

        return respuesta.content[0].text

    except Exception as e:
        return f"Error al conectar con la IA: {str(e)}"


def chat_medico_ia(db):
    st.header("Chat con IA Medica")
    st.markdown("> Asistente medico especializado con IA avanzada. Disponible 24/7.")
    st.divider()

    inicializar_chat()

    # Panel lateral del chat
    with st.sidebar:
        st.divider()
        st.markdown("**MediAssist IA**")
        st.caption("Especialidades:")
        st.caption("🧠 Neurologia")
        st.caption("👶 Pediatria")
        st.caption("💊 Farmacologia")
        st.caption("🔬 EEG")
        st.divider()

        if st.button("Limpiar conversacion"):
            st.session_state.mensajes = []
            st.rerun()

        st.divider()
        st.markdown("**Preguntas rapidas:**")

        preguntas_rapidas = [
            "Criterios de convulsion febril simple vs compleja",
            "Dosis de diazepam en estatus epileptico pediatrico",
            "Signos de alarma neurologica en lactantes",
            "Interpretacion escala Glasgow en ninos",
            "Cuando referir urgente al neurologo",
        ]

        for pregunta in preguntas_rapidas:
            if st.button(pregunta, key=f"quick_{pregunta}"):
                st.session_state.mensajes.append({
                    "rol": "user",
                    "contenido": pregunta,
                    "hora": datetime.datetime.now().strftime("%H:%M")
                })
                with st.spinner("MediAssist esta pensando..."):
                    respuesta = obtener_respuesta_ia([
                        {"rol": m["rol"], "contenido": m["contenido"]}
                        for m in st.session_state.mensajes
                    ])
                st.session_state.mensajes.append({
                    "rol": "assistant",
                    "contenido": respuesta,
                    "hora": datetime.datetime.now().strftime("%H:%M")
                })
                st.rerun()

    # Mostrar historial de mensajes
    if not st.session_state.mensajes:
        st.markdown("""
        <div style="text-align:center; padding: 40px; opacity: 0.6;">
            <h3>🧠 MediAssist</h3>
            <p>Asistente medico especializado en neurologia y pediatria.</p>
            <p>Puedes preguntarme sobre diagnosticos, tratamientos,<br>
            interpretacion de escalas, medicamentos y mas.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for mensaje in st.session_state.mensajes:
            mostrar_mensaje(mensaje["rol"], mensaje["contenido"])

    # Input del usuario
    st.divider()
    prompt = st.chat_input("Escribe tu consulta medica aqui...")

    if prompt:
        hora = datetime.datetime.now().strftime("%H:%M")
        st.session_state.mensajes.append({
            "rol": "user",
            "contenido": prompt,
            "hora": hora
        })
        mostrar_mensaje("user", prompt)

        with st.spinner("MediAssist esta analizando..."):
            respuesta = obtener_respuesta_ia([
                {"rol": m["rol"], "contenido": m["contenido"]}
                for m in st.session_state.mensajes
            ])

        st.session_state.mensajes.append({
            "rol": "assistant",
            "contenido": respuesta,
            "hora": datetime.datetime.now().strftime("%H:%M")
        })

        mostrar_mensaje("assistant", respuesta)

        # Guardar en Firebase (solo la pregunta y resumen)
        try:
            db.collection("chat_ia").add({
                "usuario": st.session_state.get("usuario", "desconocido"),
                "pregunta": prompt,
                "fecha": datetime.datetime.now()
            })
        except:
            pass

        st.rerun()
