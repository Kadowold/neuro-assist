import streamlit as st

def mostrar_perfil_sidebar():
    perfiles = {
        "Montserrath": {
            "nombre": "Dra. Montserrath",
            "especialidad": "Pediatria",
            "cedula": "Ced. Prof. 12345678",
            "hospital": "Hospital La Raza",
            "avatar": "👩‍⚕️"
        },
        "kadowold": {
            "nombre": "Admin",
            "especialidad": "Desarrollador",
            "cedula": "",
            "hospital": "NeuroApp Dev",
            "avatar": "👨‍💻"
        }
    }

    usuario = st.session_state.get("usuario", "")
    perfil = perfiles.get(usuario, {
        "nombre": usuario,
        "especialidad": "Medico",
        "cedula": "",
        "hospital": "",
        "avatar": "👤"
    })

    with st.sidebar:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            margin-bottom: 16px;
        ">
            <div style="font-size: 48px">{perfil['avatar']}</div>
            <div style="color: white; font-weight: 700; font-size: 16px; margin-top: 8px">
                {perfil['nombre']}
            </div>
            <div style="color: #90caf9; font-size: 13px">{perfil['especialidad']}</div>
            <div style="color: #64b5f6; font-size: 11px; margin-top: 4px">{perfil['cedula']}</div>
            <div style="color: #90caf9; font-size: 11px">{perfil['hospital']}</div>
        </div>
        """, unsafe_allow_html=True)


def tutorial_interactivo():
    st.header("Tutorial de NeuroApp")
    st.markdown("> Aprende a usar todas las funciones de la app en minutos.")
    st.divider()

    pasos = {
        "Inicio rapido": {
            "icono": "🚀",
            "descripcion": "Bienvenido a NeuroApp. Esta app te permite gestionar pacientes, calcular escalas clinicas, analizar EEGs y consultar con IA medica.",
            "pasos": [
                "Inicia sesion con tu usuario y contrasena",
                "Usa el menu lateral izquierdo para navegar entre modulos",
                "El boton ☀️/🌙 en la esquina superior cambia entre modo claro y oscuro",
                "Todos los datos se guardan automaticamente en la nube"
            ]
        },
        "Registrar sintomas": {
            "icono": "📝",
            "descripcion": "Registra y monitorea los sintomas neurologicos de tus pacientes.",
            "pasos": [
                "Ve a 'Registrar sintoma' en el menu",
                "Escribe el nombre exacto del paciente",
                "Selecciona el tipo de sintoma, intensidad y desencadenante",
                "Presiona 'Guardar sintoma' — se guarda en la nube instantaneamente",
                "Para ver el historial ve a 'Ver historial' y busca el nombre del paciente"
            ]
        },
        "Calculadoras clinicas": {
            "icono": "📊",
            "descripcion": "4 escalas neurologicas profesionales con interpretacion automatica.",
            "pasos": [
                "Ve a 'Calculadoras clinicas' en el menu",
                "Selecciona la escala en el menu lateral: Glasgow, NIHSS, MMSE o Rankin",
                "Ingresa el nombre del paciente",
                "Responde cada pregunta de la escala",
                "Presiona calcular — el resultado se interpreta automaticamente",
                "El resultado se guarda en Firebase para el expediente"
            ]
        },
        "Herramientas pediatricas": {
            "icono": "👶",
            "descripcion": "4 herramientas especializadas para pediatria.",
            "pasos": [
                "Calculadora de dosis: ingresa el peso y selecciona el medicamento",
                "Curvas de crecimiento: compara con tablas OMS por edad y sexo",
                "Desarrollo infantil: evalua hitos del desarrollo por edad",
                "Triaje pediatrico: determina la urgencia segun signos vitales y alarmas"
            ]
        },
        "Signos vitales": {
            "icono": "💓",
            "descripcion": "Semaforo visual de signos vitales por edad.",
            "pasos": [
                "Ve a 'Signos vitales' en el menu",
                "Selecciona la edad del paciente en meses o anos",
                "Ingresa todos los signos vitales medidos",
                "El semaforo muestra Verde/Amarillo/Rojo automaticamente",
                "Se generan los rangos normales especificos para esa edad"
            ]
        },
        "Visualizador EEG": {
            "icono": "🔬",
            "descripcion": "Analiza electroencefalogramas con inteligencia artificial.",
            "pasos": [
                "Ve a 'Visualizador EEG' en el menu",
                "Modo demo: selecciona un tipo de EEG simulado para practicar",
                "Modo real: sube un archivo .edf del electroencefalografo",
                "La IA analiza las bandas de frecuencia automaticamente",
                "Se detectan picos anormales y posible actividad epileptiforme",
                "El resultado se guarda en el expediente del paciente"
            ]
        },
        "Expediente clinico": {
            "icono": "📋",
            "descripcion": "Historial completo unificado de cada paciente.",
            "pasos": [
                "Ve a 'Expediente clinico' en el menu",
                "Escribe el nombre exacto del paciente y presiona 'Cargar expediente'",
                "Navega por las pestanas: Sintomas, Calculadoras, Pediatria, EEG",
                "En la pestana 'Exportar PDF' genera un reporte completo profesional",
                "El PDF incluye todos los registros organizados por seccion"
            ]
        },
        "Chat IA Medica": {
            "icono": "🧠",
            "descripcion": "Asistente medico con IA avanzada disponible 24/7.",
            "pasos": [
                "Ve a 'Chat IA Medica' en el menu",
                "Escribe tu consulta medica en el campo de texto inferior",
                "Usa las preguntas rapidas del panel lateral para consultas frecuentes",
                "La IA responde con informacion basada en evidencia medica",
                "Presiona 'Limpiar conversacion' para iniciar una nueva consulta",
                "Nota: requiere creditos activos en la cuenta de Anthropic"
            ]
        },
        "Dashboard": {
            "icono": "📈",
            "descripcion": "Estadisticas globales de todos tus pacientes.",
            "pasos": [
                "Ve a 'Dashboard' en el menu",
                "Ve estadisticas generales: total pacientes, sintomas, calculadoras",
                "Explora las graficas por pestana: Sintomas, Calculadoras, Pediatria, EEG",
                "Los datos se actualizan en tiempo real desde Firebase"
            ]
        }
    }

    modulo_sel = st.selectbox("Selecciona el modulo que quieres aprender",
                              list(pasos.keys()))

    modulo = pasos[modulo_sel]
    st.divider()

    st.markdown(f"## {modulo['icono']} {modulo_sel}")
    st.info(modulo["descripcion"])

    st.subheader("Pasos:")
    for i, paso in enumerate(modulo["pasos"], 1):
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e3a5f22, #2d6a9f22);
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
        ">
            <span style="color: #60a5fa; font-weight: 700">Paso {i}:</span>
            <span style="margin-left: 8px">{paso}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.success("Tip: Todos los datos se sincronizan en tiempo real con Firebase. Puedes acceder desde cualquier dispositivo con internet.")
