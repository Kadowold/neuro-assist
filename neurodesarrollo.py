import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

HITOS_NEURODESARROLLO = {
    1: {
        "Motor grueso": ["Levanta cabeza brevemente boca abajo"],
        "Motor fino": ["Abre manos reflejamente"],
        "Lenguaje": ["Llanto diferenciado", "Sonidos guturales"],
        "Social": ["Fija la mirada en rostros", "Responde a voz familiar"]
    },
    2: {
        "Motor grueso": ["Levanta cabeza 45 grados boca abajo", "Controla cabeza brevemente sentado"],
        "Motor fino": ["Abre y cierra manos", "Lleva manos a la boca"],
        "Lenguaje": ["Arrullos y vocalizaciones", "Reacciona a sonidos fuertes"],
        "Social": ["Sonrisa social", "Sigue objetos con la vista 180 grados"]
    },
    4: {
        "Motor grueso": ["Sostiene cabeza firmemente", "Se apoya en antebrazos boca abajo", "Rolado parcial"],
        "Motor fino": ["Alcanza objetos voluntariamente", "Sostiene objetos brevemente"],
        "Lenguaje": ["Rie a carcajadas", "Balbucea vocales"],
        "Social": ["Reconoce cuidadores", "Disfruta interaccion social"]
    },
    6: {
        "Motor grueso": ["Se sienta con apoyo", "Se voltea de boca arriba a boca abajo", "Apoyo en manos sentado"],
        "Motor fino": ["Pasa objetos de mano en mano", "Pinza inferior emergente"],
        "Lenguaje": ["Consonantes ba ma pa", "Responde a su nombre"],
        "Social": ["Reconoce caras familiares vs extranios", "Imita expresiones faciales"]
    },
    9: {
        "Motor grueso": ["Se sienta sin apoyo estable", "Gatea o arrastra", "Se pone de pie con apoyo"],
        "Motor fino": ["Pinza inferior", "Golpea objetos entre si", "Indice senalador emergente"],
        "Lenguaje": ["Mama papa con significado", "Entiende NO", "Imita sonidos"],
        "Social": ["Ansiedad ante extranios", "Juego de escondidas", "Senala con el dedo"]
    },
    12: {
        "Motor grueso": ["Camina con apoyo o solo", "Se pone de pie solo", "Sube escalones gateando"],
        "Motor fino": ["Pinza superior fina", "Introduce objetos en recipientes", "Garabatea"],
        "Lenguaje": ["2 a 3 palabras con significado", "Entiende ordenes simples", "Apunta para pedir"],
        "Social": ["Juego imitativo", "Usa objetos correctamente", "Muestra objetos a adultos"]
    },
    15: {
        "Motor grueso": ["Camina solo bien", "Sube escaleras con apoyo", "Se agacha y se levanta"],
        "Motor fino": ["Apila 2 cubos", "Mete y saca objetos", "Usa cuchara torpemente"],
        "Lenguaje": ["5 a 10 palabras", "Jerga con entonacion", "Senala partes del cuerpo"],
        "Social": ["Juego simbolico simple", "Muestra afecto", "Imita tareas del hogar"]
    },
    18: {
        "Motor grueso": ["Corre torpemente", "Sube escaleras con apoyo alternando", "Patea pelota"],
        "Motor fino": ["Apila 3 a 4 cubos", "Garabatea espontaneamente", "Pasa paginas"],
        "Lenguaje": ["10 a 20 palabras", "Senala imagenes en libros", "Dice NO con intencion"],
        "Social": ["Juego simbolico", "Imita actividades", "Busca aprobacion adultos"]
    },
    24: {
        "Motor grueso": ["Corre bien", "Sube y baja escaleras con apoyo", "Salta en dos pies"],
        "Motor fino": ["Apila 6 cubos", "Hace trazos circulares", "Usa tenedor"],
        "Lenguaje": ["Frases de 2 palabras minimo", "50 palabras o mas", "Extraños entienden 50 por ciento"],
        "Social": ["Juego paralelo", "Imita a otros ninos", "Conciencia de si mismo"]
    }
}

SENALES_ALARMA_ABSOLUTAS = [
    "No fija la mirada a los 2 meses",
    "No sonrie a los 3 meses",
    "No sostiene la cabeza a los 4 meses",
    "No balbucea a los 6 meses",
    "No se sienta a los 9 meses",
    "No dice ninguna palabra a los 12 meses",
    "No camina a los 18 meses",
    "No dice frases de 2 palabras a los 24 meses",
    "Perdida de habilidades previamente adquiridas (REGRESION)",
    "No responde a su nombre a los 12 meses",
    "No senala con el dedo a los 14 meses",
    "No hace juego simbolico a los 18 meses"
]

def analizar_regresion_ia(paciente, historial_hitos, edad_actual):
    try:
        import anthropic
        api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
        cliente = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Eres un neuropediatra experto en neurodesarrollo infantil.

Analiza el siguiente historial de hitos del neurodesarrollo del paciente y detecta patrones de regresión, retraso o riesgo:

PACIENTE: {paciente}
EDAD ACTUAL: {edad_actual} meses

HISTORIAL DE EVALUACIONES:
{historial_hitos}

Genera un reporte con estas secciones:

## ANALISIS DEL NEURODESARROLLO

### Estado actual por area
Evalua Motor grueso, Motor fino, Lenguaje y Social.

### Patrones detectados
Describe tendencias, retrasos o regresiones encontradas.

### Nivel de riesgo
NORMAL / RETRASO LEVE / RETRASO MODERADO / REGRESION DETECTADA / RIESGO ALTO

### Alertas especificas
Lista de hallazgos que requieren atención.

### Diagnosticos a considerar
Si hay senales de alarma, menciona condiciones a descartar como:
- Trastorno del Espectro Autista (TEA)
- Paralisis cerebral
- Errores innatos del metabolismo
- Hipoacusia
- Retraso global del desarrollo
- Sindrome de Rett u otras condiciones regresivas

### Estudios recomendados
Examenes especificos segun el perfil de riesgo.

### Plan de seguimiento
Frecuencia de evaluación y especialistas a consultar.

Se preciso, basate en criterios DSM-5, ICD-11 y guias de la AAP."""

        respuesta = cliente.messages.create(
            model="claude-opus-4-6",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.content[0].text
    except Exception as e:
        return f"Error al analizar: {str(e)}"


def monitor_neurodesarrollo(db):
    st.header("Monitor de Neurodesarrollo")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1628, #1a3a6e);
        border: 1px solid #c9a84c44;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="color: #f0c96e; font-weight: 600; font-size: 15px">
            🧠 Monitor Inteligente de Hitos y Regresión Neurologica
        </div>
        <div style="color: #8ba3cc; font-size: 13px; margin-top: 4px">
            Vigilancia predictiva del neurodesarrollo para bebes de 0 a 24 meses.
            Detecta retrasos y regresiones neurologicas con alertas automaticas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📝 Nueva evaluación",
        "📊 Tablero predictivo",
        "🚨 Alertas de regresión"
    ])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            paciente = st.text_input("Nombre del bebe", key="nd_paciente")
            edad_meses = st.selectbox("Edad actual (meses)", [1, 2, 4, 6, 9, 12, 15, 18, 24])
        with col2:
            sexo = st.radio("Sexo", ["Masculino", "Femenino"], horizontal=True)
            prematuro = st.checkbox("Nacio prematuro (ajustar edad)")
            if prematuro:
                semanas_prematuro = st.number_input("Semanas de prematurez", 1, 16, 4)
                edad_corregida = max(1, edad_meses - (semanas_prematuro // 4))
                st.info(f"Edad corregida: {edad_corregida} meses")
            else:
                edad_corregida = edad_meses

        st.divider()
        st.subheader(f"Hitos esperados a los {edad_meses} meses")

        edad_ref = min(HITOS_NEURODESARROLLO.keys(),
                      key=lambda x: abs(x - edad_corregida))
        hitos_edad = HITOS_NEURODESARROLLO[edad_ref]

        resultados = {}
        total_hitos = 0
        hitos_cumplidos = 0

        for area, hitos_lista in hitos_edad.items():
            icono = {"Motor grueso": "🏃", "Motor fino": "✋",
                    "Lenguaje": "💬", "Social": "👥"}.get(area, "⭐")
            st.markdown(f"### {icono} {area}")
            resultados[area] = {}
            for hito in hitos_lista:
                cumple = st.checkbox(hito, key=f"nd_{edad_meses}_{area}_{hito}")
                resultados[area][hito] = cumple
                total_hitos += 1
                if cumple:
                    hitos_cumplidos += 1

        st.divider()
        st.subheader("Señales de alarma absoluta")
        st.markdown("*Marca si alguna aplica al paciente*")
        alarmas_presentes = []
        for senal in SENALES_ALARMA_ABSOLUTAS:
            if st.checkbox(senal, key=f"alarma_{senal}"):
                alarmas_presentes.append(senal)

        notas_clinicas = st.text_area(
            "Notas clinicas adicionales",
            placeholder="Observaciones del medico durante la evaluacion..."
        )

        if st.button("Guardar evaluacion y analizar con IA", use_container_width=True):
            if paciente == "":
                st.warning("Ingresa el nombre del bebe.")
            else:
                porcentaje = (hitos_cumplidos / total_hitos * 100) if total_hitos > 0 else 0

                evaluacion = {
                    "paciente": paciente,
                    "edad_meses": edad_meses,
                    "edad_corregida": edad_corregida,
                    "sexo": sexo,
                    "prematuro": prematuro,
                    "hitos_cumplidos": hitos_cumplidos,
                    "total_hitos": total_hitos,
                    "porcentaje": round(porcentaje, 1),
                    "resultados_por_area": {
                        area: sum(1 for v in hitos.values() if v)
                        for area, hitos in resultados.items()
                    },
                    "alarmas_presentes": alarmas_presentes,
                    "notas": notas_clinicas,
                    "fecha": datetime.datetime.now(),
                    "medico": st.session_state.get("usuario", "")
                }

                try:
                    db.collection("neurodesarrollo").add(evaluacion)
                    st.success("Evaluación guardada.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric("Hitos cumplidos", f"{hitos_cumplidos}/{total_hitos}")
                col2.metric("Porcentaje", f"{porcentaje:.0f}%")
                col3.metric("Alarmas", len(alarmas_presentes))

                if alarmas_presentes or porcentaje < 60:
                    st.error("🚨 ALERTA DE REGRESIÓN O RETRASO DETECTADA")

                with st.spinner("Analizando neurodesarrollo con IA..."):
                    try:
                        docs = db.collection("neurodesarrollo").where(
                            "paciente", "==", paciente
                        ).stream()
                        historial = []
                        for doc in docs:
                            d = doc.to_dict()
                            historial.append(
                                f"Edad {d.get('edad_meses')}m: "
                                f"{d.get('porcentaje')}% hitos, "
                                f"Alarmas: {d.get('alarmas_presentes', [])}"
                            )
                        analisis = analizar_regresion_ia(
                            paciente,
                            "\n".join(historial) if historial else "Primera evaluación",
                            edad_meses
                        )
                        st.markdown(analisis)
                    except Exception as e:
                        st.error(f"Error en analisis: {e}")

    with tab2:
        st.subheader("Tablero predictivo de neurodesarrollo")
        paciente_tablero = st.text_input("Nombre del bebe", key="nd_tablero")

        if paciente_tablero:
            try:
                docs = db.collection("neurodesarrollo").where(
                    "paciente", "==", paciente_tablero
                ).stream()

                evaluaciones = []
                for doc in docs:
                    d = doc.to_dict()
                    if "fecha" in d and d["fecha"]:
                        try:
                            d["fecha"] = d["fecha"].strftime("%Y-%m-%d")
                        except:
                            pass
                    evaluaciones.append(d)

                if not evaluaciones:
                    st.info("Sin evaluaciones para este bebe.")
                else:
                    evaluaciones.sort(key=lambda x: x.get("edad_meses", 0))

                    edades = [e["edad_meses"] for e in evaluaciones]
                    porcentajes = [e["porcentaje"] for e in evaluaciones]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=edades, y=[80] * len(edades),
                        fill=None, mode="lines",
                        line=dict(color="#40916c", width=0),
                        name="Zona normal superior"
                    ))
                    fig.add_trace(go.Scatter(
                        x=edades, y=[60] * len(edades),
                        fill="tonexty", mode="lines",
                        line=dict(color="#40916c", width=0),
                        fillcolor="rgba(64,145,108,0.2)",
                        name="Zona normal"
                    ))
                    fig.add_trace(go.Scatter(
                        x=edades, y=porcentajes,
                        mode="lines+markers",
                        name="Desarrollo del bebe",
                        line=dict(color="#c9a84c", width=3),
                        marker=dict(size=10, color="#f0c96e",
                                  line=dict(color="#c9a84c", width=2))
                    ))
                    fig.add_hline(y=60, line_dash="dash",
                                line_color="#e63946",
                                annotation_text="Umbral de alerta")

                    fig.update_layout(
                        title=f"Trayectoria de neurodesarrollo — {paciente_tablero}",
                        xaxis_title="Edad (meses)",
                        yaxis_title="Hitos cumplidos (%)",
                        plot_bgcolor="#0a1628",
                        paper_bgcolor="#0d1f3c",
                        font=dict(color="#e8f0fe"),
                        yaxis=dict(range=[0, 105]),
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Progreso por area")
                    ultima = evaluaciones[-1]
                    areas = ultima.get("resultados_por_area", {})
                    hitos_por_area = HITOS_NEURODESARROLLO.get(
                        min(HITOS_NEURODESARROLLO.keys(),
                            key=lambda x: abs(x - ultima.get("edad_meses", 12))), {})

                    cols = st.columns(4)
                    iconos = {"Motor grueso": "🏃", "Motor fino": "✋",
                             "Lenguaje": "💬", "Social": "👥"}
                    for i, (area, cumplidos) in enumerate(areas.items()):
                        total_area = len(hitos_por_area.get(area, [1]))
                        pct = (cumplidos / total_area * 100) if total_area > 0 else 0
                        icono = iconos.get(area, "⭐")
                        color = "#40916c" if pct >= 70 else "#f4a261" if pct >= 50 else "#e63946"
                        cols[i % 4].markdown(f"""
                        <div style="
                            background: #0d1f3c;
                            border: 1px solid {color}66;
                            border-radius: 10px;
                            padding: 12px;
                            text-align: center;
                        ">
                            <div style="font-size: 24px">{icono}</div>
                            <div style="color: {color}; font-weight: 700; font-size: 18px">{pct:.0f}%</div>
                            <div style="color: #8ba3cc; font-size: 11px">{area}</div>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Alertas de regresión neurologica")
        try:
            docs = db.collection("neurodesarrollo").stream()
            alertas = []
            for doc in docs:
                d = doc.to_dict()
                if d.get("alarmas_presentes") or d.get("porcentaje", 100) < 60:
                    if "fecha" in d and d["fecha"]:
                        try:
                            d["fecha"] = d["fecha"].strftime("%Y-%m-%d")
                        except:
                            pass
                    alertas.append(d)

            if not alertas:
                st.success("Sin alertas de regresión activas.")
            else:
                st.error(f"🚨 {len(alertas)} alerta(s) de regresión detectada(s)")
                for alerta in alertas:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #2d0000, #4a0d0d);
                        border: 2px solid #e63946;
                        border-radius: 12px;
                        padding: 16px;
                        margin: 8px 0;
                    ">
                        <div style="color: #ff6b6b; font-weight: 700; font-size: 15px">
                            🚨 {alerta.get('paciente')} — {alerta.get('edad_meses')} meses
                        </div>
                        <div style="color: #fca5a5; font-size: 12px">
                            Hitos: {alerta.get('porcentaje')}% | Fecha: {alerta.get('fecha')}
                        </div>
                        <div style="color: #fecaca; font-size: 12px; margin-top: 6px">
                            Alarmas: {', '.join(alerta.get('alarmas_presentes', ['Porcentaje bajo']))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
