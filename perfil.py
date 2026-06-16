import streamlit as st


def mostrar_perfil_sidebar():
    perfiles = {
        "Montserrath": {
            "nombre": "Dra. Montserrath",
            "especialidad": "Pediatria",
            "cedula": "Ced. Prof. 12345678",
            "hospital": "Hospital La Raza",
            "avatar": "👩🏻‍⚕️",
        },
        "kadowold": {
            "nombre": "Admin",
            "especialidad": "Desarrollador",
            "cedula": "",
            "hospital": "NeuroApp Dev",
            "avatar": "👨‍💻",
        },
    }

    usuario = st.session_state.get("usuario", "")
    perfil = perfiles.get(
        usuario,
        {
            "nombre": usuario,
            "especialidad": "Medico",
            "cedula": "",
            "hospital": "",
            "avatar": "👤",
        },
    )

    with st.sidebar:
        st.markdown(
            f"""
<div style="
    background: linear-gradient(135deg, #0a1628 0%, #1a3a6e 100%);
    border: 1px solid #c9a84c44;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    margin-bottom: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
">
    <div style="
        font-size: 52px;
        background: #c9a84c22;
        border: 2px solid #c9a84c66;
        border-radius: 50%;
        width: 72px;
        height: 72px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
        box-shadow: 0 0 20px #c9a84c44;
    ">{perfil['avatar']}</div>
    <div style="
        color: #f0c96e;
        font-weight: 700;
        font-size: 15px;
    ">{perfil['nombre']}</div>
    <div style="
        color: #8ba3cc;
        font-size: 12px;
        margin-top: 3px;
    ">{perfil['especialidad']}</div>
    <div style="
        color: #c9a84c88;
        font-size: 11px;
        margin-top: 2px;
    ">{perfil['cedula']}</div>
    <div style="
        background: #c9a84c22;
        border: 1px solid #c9a84c44;
        border-radius: 6px;
        padding: 3px 8px;
        color: #c9a84c;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1px;
        margin-top: 8px;
        display: inline-block;
    ">● EN LINEA</div>
</div>
""",
            unsafe_allow_html=True,
        )


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
                "El boton del sol/luna en la esquina superior cambia entre modo claro y oscuro",
                "Todos los datos se guardan automaticamente en la nube",
            ],
        },
        "Registrar sintomas": {
            "icono": "📝",
            "descripcion": "Registra y monitorea los sintomas neurologicos de tus pacientes.",
            "pasos": [
                "Ve a 'Registrar sintoma' en el menu",
                "Escribe el nombre exacto del paciente",
                "Selecciona el tipo de sintoma, intensidad y desencadenante",
                "Presiona 'Guardar sintoma' — se guarda en la nube instantaneamente",
                "Para ver el historial ve a 'Ver historial' y busca el nombre del paciente",
            ],
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
                "El resultado se guarda en Firebase para el expediente",
            ],
        },
        "Herramientas pediatricas": {
            "icono": "👶",
            "descripcion": "4 herramientas especializadas para pediatria.",
            "pasos": [
                "Calculadora de dosis: ingresa el peso y selecciona el medicamento",
                "Curvas de crecimiento: compara con tablas OMS por edad y sexo",
                "Desarrollo infantil: evalua hitos del desarrollo por edad",
                "Triaje pediatrico: determina la urgencia segun signos vitales y alarmas",
            ],
        },
        "Signos vitales": {
            "icono": "💓",
            "descripcion": "Semaforo visual de signos vitales por edad.",
            "pasos": [
                "Ve a 'Signos vitales' en el menu",
                "Selecciona la edad del paciente en meses o anos",
                "Ingresa todos los signos vitales medidos",
                "El semaforo muestra Verde/Amarillo/Rojo automaticamente",
                "Se generan los rangos normales especificos para esa edad",
            ],
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
                "El resultado se guarda en el expediente del paciente",
            ],
        },
        "Expediente clinico": {
            "icono": "📋",
            "descripcion": "Historial completo unificado de cada paciente.",
            "pasos": [
                "Ve a 'Expediente clinico' en el menu",
                "Escribe el nombre exacto del paciente y presiona 'Cargar expediente'",
                "Navega por las pestanas: Sintomas, Calculadoras, Pediatria, EEG",
                "En la pestana 'Exportar PDF' genera un reporte completo profesional",
                "El PDF incluye todos los registros organizados por seccion",
            ],
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
                "Nota: requiere creditos activos en la cuenta de Anthropic",
            ],
        },
        "Dashboard": {
            "icono": "📈",
            "descripcion": "Estadisticas globales de todos tus pacientes.",
            "pasos": [
                "Ve a 'Dashboard' en el menu",
                "Ve estadisticas generales: total pacientes, sintomas, calculadoras",
                "Explora las graficas por pestana: Sintomas, Calculadoras, Pediatria, EEG",
                "Los datos se actualizan en tiempo real desde Firebase",
            ],
        },
        "Agenda medica": {
            "icono": "📅",
            "descripcion": "Gestiona citas y seguimientos de tus pacientes con un sistema completo de agenda.",
            "pasos": [
                "Ve a 'Agenda medica' en el menu",
                "Pestana 'Nueva cita': ingresa nombre del paciente, fecha, hora y tipo de cita",
                "Selecciona la prioridad: Normal, Alta o Urgente",
                "Escribe el motivo de la cita y notas adicionales",
                "Presiona 'Guardar cita' — se guarda en Firebase automaticamente",
                "Pestana 'Ver agenda': filtra citas por rango de fechas",
                "Puedes marcar citas como completadas, cancelarlas o eliminarlas",
                "Pestana 'Proximas citas': ve rapidamente las citas de hoy y manana",
            ],
        },
        "Notas por voz": {
            "icono": "🎙️",
            "descripcion": "Dicta tus notas medicas con voz y la IA las transcribe y redacta profesionalmente.",
            "pasos": [
                "Ve a 'Notas por voz' en el menu",
                "Ingresa el nombre del paciente",
                "Selecciona el tipo de nota: Evolucion, Historia clinica, Urgencias, Resumen",
                "Opcion 1 - Audio: graba desde tu celular con la app de grabadora de voz",
                "Sube el archivo de audio (WAV, MP3, M4A, OGG)",
                "Presiona 'Transcribir audio' — Whisper AI transcribe automaticamente",
                "Edita la transcripcion si es necesario",
                "Presiona 'Mejorar con IA' — Claude redacta la nota profesionalmente",
                "Opcion 2 - Texto: escribe directamente y presiona 'Mejorar texto con IA'",
                "Guarda la nota en Firebase o descargala en PDF",
                "Pestana 'Notas guardadas': busca notas anteriores por paciente",
            ],
        },
        "Predictor de riesgo IA": {
            "icono": "🔍",
            "descripcion": "Analiza todos los datos del paciente con IA y predice riesgos neurologicos futuros.",
            "pasos": [
                "Ve a 'Predictor de riesgo IA' en el menu",
                "Escribe el nombre exacto del paciente como esta registrado en el sistema",
                "Ingresa edad, sexo y antecedentes familiares relevantes",
                "Presiona 'Analizar y predecir riesgo con IA'",
                "La IA recopila TODOS los datos del paciente en Firebase",
                "Genera un reporte con 9 secciones: riesgos, patrones, predicciones, recomendaciones",
                "Guarda el reporte en Firebase o descargalo en PDF",
                "Entre mas datos tenga el paciente, mas precisa sera la prediccion",
            ],
        },  
        "Monitor criticos": {
            "icono": "🚨",
            "descripcion": "Monitorea en tiempo real todos los pacientes con alertas criticas o advertencias.",
            "pasos": [
                "Ve a 'Monitor criticos' en el menu — aparece segundo en la lista por su importancia",
                "El monitor revisa automaticamente: signos vitales, triaje, EEG y escalas clinicas",
                "Alertas ROJAS: pacientes en estado critico que requieren atencion inmediata",
                "Alertas AMARILLAS: pacientes con parametros fuera de rango que requieren vigilancia",
                "Si no hay alertas veras una pantalla verde confirmando que todo esta normal",
                "Presiona 'Actualizar monitor' para refrescar los datos en tiempo real",
                "Revisa este modulo al inicio de cada turno para identificar pacientes prioritarios",
            ],
        },
        "Diagnostico diferencial IA": {
            "icono": "🔍",
            "descripcion": "Describe los sintomas del paciente y la IA genera un diagnostico diferencial completo con probabilidades.",
            "pasos": [
                "Ve a 'Diagnostico diferencial IA' en el menu",
                "Ingresa nombre, edad, sexo y enfoque clinico del paciente",
                "Selecciona el tiempo de evolución del cuadro clinico",
                "Describe los sintomas principales con el mayor detalle posible",
                "Agrega signos vitales, hallazgos de exploración fisica y estudios previos",
                "Presiona 'Generar diagnostico diferencial con IA'",
                "La IA genera hasta 4 diagnosticos ordenados por probabilidad",
                "Incluye: criterios a favor, criterios en contra y accion inmediata por cada diagnostico",
                "Al final muestra diagnosticos criticos a descartar, plan de estudio y signos de alarma",
                "Guarda el resultado en Firebase o descargalo en PDF",
            ],
        },
        "Estadisticas clinica": {
            "icono": "📊",
            "descripcion": "Analiza tendencias historicas y genera proyecciones predictivas de tu clinica con IA.",
            "pasos": [
                "Ve a 'Estadisticas clinica' en el menu",
                "Pestana 'Tendencias': graficas de sintomas por mes, frecuencia y intensidad promedio",
                "Pestana 'Predicciones': presiona 'Generar proyecciones con IA' para proyecciones del proximo mes",
                "La IA analiza patrones estacionales y proyecta carga de pacientes futura",
                "Pestana 'Carga clinica': distribucion de urgencias, tipos de cita y total de consultas",
                "Pestana 'Farmacologia': medicamentos mas usados y distribucion de peso de pacientes",
                "Entre mas datos esten registrados en la app, mas precisas seran las proyecciones",
                "Usa las proyecciones para planificar insumos y carga de trabajo",
            ],
        },
    }

    modulo_sel = st.selectbox(
        "Selecciona el modulo que quieres aprender", list(pasos.keys())
    )

    modulo = pasos[modulo_sel]
    st.divider()

    st.markdown(f"## {modulo['icono']} {modulo_sel}")
    st.info(modulo["descripcion"])

    st.subheader("Pasos:")
    for i, paso in enumerate(modulo["pasos"], 1):
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, rgba(10, 22, 40, 0.1), rgba(26, 58, 110, 0.1));
            border-left: 4px solid #c9a84c;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
        ">
            <span style="color: #f0c96e; font-weight: 700">Paso {i}:</span>
            <span style="margin-left: 8px; color: inherit;">{paso}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.success(
        "Tip: Todos los datos se sincronizan en tiempo real con Firebase. Puedes acceder desde cualquier dispositivo con internet."
    )
