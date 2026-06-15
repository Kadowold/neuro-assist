import streamlit as st

def escala_glasgow():
    st.header("Escala de Coma de Glasgow")
    st.markdown("""
    > Evalua el nivel de consciencia del paciente.
    > **Puntaje minimo: 3 | Puntaje maximo: 15**
    """)
    st.divider()

    st.subheader("1. Apertura ocular")
    ocular = st.radio("Selecciona la respuesta:", [
        "4 - Espontanea",
        "3 - Al llamado verbal",
        "2 - Al estimulo doloroso",
        "1 - Sin respuesta"
    ], key="glasgow_ocular")

    st.subheader("2. Respuesta verbal")
    verbal = st.radio("Selecciona la respuesta:", [
        "5 - Orientado",
        "4 - Confuso",
        "3 - Palabras inapropiadas",
        "2 - Sonidos incomprensibles",
        "1 - Sin respuesta"
    ], key="glasgow_verbal")

    st.subheader("3. Respuesta motora")
    motora = st.radio("Selecciona la respuesta:", [
        "6 - Obedece ordenes",
        "5 - Localiza el dolor",
        "4 - Retira al dolor",
        "3 - Flexion anormal",
        "2 - Extension anormal",
        "1 - Sin respuesta"
    ], key="glasgow_motora")

    if st.button("Calcular Glasgow"):
        p_ocular = int(ocular[0])
        p_verbal = int(verbal[0])
        p_motora = int(motora[0])
        total = p_ocular + p_verbal + p_motora

        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ocular", p_ocular, "/4")
        col2.metric("Verbal", p_verbal, "/5")
        col3.metric("Motora", p_motora, "/6")
        col4.metric("TOTAL", total, "/15")

        st.divider()
        if total >= 13:
            st.success(f"Puntaje {total}/15 — TCE LEVE: Paciente consciente. Monitoreo rutinario.")
        elif total >= 9:
            st.warning(f"Puntaje {total}/15 — TCE MODERADO: Requiere observacion hospitalaria.")
        else:
            st.error(f"Puntaje {total}/15 — TCE GRAVE: Riesgo vital. Manejo en UCI inmediato.")

        st.info("Desglose: E" + str(p_ocular) + " V" + str(p_verbal) + " M" + str(p_motora))


def escala_nihss():
    st.header("Escala NIHSS")
    st.markdown("""
    > National Institutes of Health Stroke Scale.
    > Evalua la severidad de un ACV (Accidente Cerebrovascular).
    > **Puntaje 0 = normal | Mayor puntaje = mayor deficit neurologico**
    """)
    st.divider()

    items = {
        "1a. Nivel de consciencia": ["0 - Alerta", "1 - Somnoliento", "2 - Estuporoso", "3 - Coma"],
        "1b. Preguntas de orientacion (mes y edad)": ["0 - Ambas correctas", "1 - Una correcta", "2 - Ninguna correcta"],
        "1c. Comandos (abrir/cerrar ojos, mano)": ["0 - Ambos correctos", "1 - Uno correcto", "2 - Ninguno correcto"],
        "2. Mirada conjugada": ["0 - Normal", "1 - Paralisis parcial", "2 - Desviacion forzada"],
        "3. Campos visuales": ["0 - Sin perdida", "1 - Hemianopsia parcial", "2 - Hemianopsia completa", "3 - Ceguera bilateral"],
        "4. Paralisis facial": ["0 - Normal", "1 - Paralisis menor", "2 - Paralisis parcial", "3 - Paralisis completa"],
        "5a. Motor brazo izquierdo": ["0 - Sin caida", "1 - Cae antes de 10s", "2 - Esfuerzo contra gravedad", "3 - Sin esfuerzo contra gravedad", "4 - Sin movimiento"],
        "5b. Motor brazo derecho": ["0 - Sin caida", "1 - Cae antes de 10s", "2 - Esfuerzo contra gravedad", "3 - Sin esfuerzo contra gravedad", "4 - Sin movimiento"],
        "6a. Motor pierna izquierda": ["0 - Sin caida", "1 - Cae antes de 5s", "2 - Esfuerzo contra gravedad", "3 - Sin esfuerzo contra gravedad", "4 - Sin movimiento"],
        "6b. Motor pierna derecha": ["0 - Sin caida", "1 - Cae antes de 5s", "2 - Esfuerzo contra gravedad", "3 - Sin esfuerzo contra gravedad", "4 - Sin movimiento"],
        "7. Ataxia de extremidades": ["0 - Ausente", "1 - Una extremidad", "2 - Dos extremidades"],
        "8. Sensibilidad": ["0 - Normal", "1 - Perdida leve", "2 - Perdida severa"],
        "9. Lenguaje": ["0 - Normal", "1 - Afasia leve", "2 - Afasia severa", "3 - Mudo"],
        "10. Disartria": ["0 - Normal", "1 - Leve", "2 - Severa"],
        "11. Extincion e inatension": ["0 - Normal", "1 - Inatension en una modalidad", "2 - Hemiinatension profunda"]
    }

    puntajes = []
    for nombre, opciones in items.items():
        st.subheader(nombre)
        seleccion = st.radio("", opciones, key=f"nihss_{nombre}")
        puntajes.append(int(seleccion[0]))
        st.markdown("---")

    if st.button("Calcular NIHSS"):
        total = sum(puntajes)
        st.divider()
        st.metric("Puntaje NIHSS Total", total, "/42")
        st.divider()

        if total == 0:
            st.success("Puntaje 0 — SIN DEFICIT: Examen neurologico normal.")
        elif total <= 4:
            st.success(f"Puntaje {total} — ACV LEVE: Deficit minimo.")
        elif total <= 15:
            st.warning(f"Puntaje {total} — ACV MODERADO: Deficit neurologico significativo.")
        elif total <= 20:
            st.error(f"Puntaje {total} — ACV MODERADO-GRAVE: Considerar trombectomia.")
        else:
            st.error(f"Puntaje {total} — ACV GRAVE: Manejo urgente en UCI.")


def escala_mini_mental():
    st.header("Mini-Mental State Examination (MMSE)")
    st.markdown("""
    > Evalua el estado cognitivo del paciente.
    > Detecta deterioro cognitivo y demencia.
    > **Puntaje maximo: 30**
    """)
    st.divider()

    st.subheader("1. Orientacion temporal (5 puntos)")
    temporal = st.slider("Cuantas preguntas respondio correctamente? (año, mes, dia, hora, estacion)", 0, 5, 0)

    st.subheader("2. Orientacion espacial (5 puntos)")
    espacial = st.slider("Cuantas preguntas respondio correctamente? (pais, ciudad, hospital, piso, servicio)", 0, 5, 0)

    st.subheader("3. Registro de palabras (3 puntos)")
    st.markdown("*Decir 3 palabras (pelota, bandera, arbol) y pedir que las repita*")
    registro = st.slider("Cuantas palabras repitio correctamente?", 0, 3, 0)

    st.subheader("4. Atencion y calculo (5 puntos)")
    st.markdown("*Restar 7 desde 100 cinco veces consecutivas (93, 86, 79, 72, 65)*")
    calculo = st.slider("Cuantas sustracciones correctas?", 0, 5, 0)

    st.subheader("5. Memoria diferida (3 puntos)")
    st.markdown("*Pedir que recuerde las 3 palabras anteriores*")
    memoria = st.slider("Cuantas palabras recuerda?", 0, 3, 0)

    st.subheader("6. Lenguaje - Nombrar objetos (2 puntos)")
    st.markdown("*Mostrar lapiz y reloj*")
    nombrar = st.slider("Cuantos objetos nombro correctamente?", 0, 2, 0)

    st.subheader("7. Repeticion (1 punto)")
    st.markdown('*Repetir: "ni si, ni no, ni pero"*')
    repeticion = st.radio("Repitio correctamente?", ["1 - Si", "0 - No"], key="mmse_rep")
    p_repeticion = int(repeticion[0])

    st.subheader("8. Comprension (3 puntos)")
    st.markdown("*Tomar papel con mano derecha, doblarlo, ponerlo en el suelo*")
    comprension = st.slider("Cuantos pasos realizo correctamente?", 0, 3, 0)

    st.subheader("9. Lectura (1 punto)")
    st.markdown('*Mostrar tarjeta que dice "Cierre los ojos"*')
    lectura = st.radio("Obedecio la orden?", ["1 - Si", "0 - No"], key="mmse_lec")
    p_lectura = int(lectura[0])

    st.subheader("10. Escritura (1 punto)")
    st.markdown("*Pedir que escriba una oracion completa*")
    escritura = st.radio("Escribio una oracion con sentido?", ["1 - Si", "0 - No"], key="mmse_esc")
    p_escritura = int(escritura[0])

    st.subheader("11. Copia de figura (1 punto)")
    st.markdown("*Copiar dos pentagonos entrelazados*")
    figura = st.radio("Copio la figura correctamente?", ["1 - Si", "0 - No"], key="mmse_fig")
    p_figura = int(figura[0])

    if st.button("Calcular MMSE"):
        total = (temporal + espacial + registro + calculo + memoria +
                 nombrar + p_repeticion + comprension + p_lectura +
                 p_escritura + p_figura)
        st.divider()
        st.metric("Puntaje MMSE Total", total, "/30")
        st.divider()

        if total >= 27:
            st.success(f"Puntaje {total}/30 — NORMAL: Sin deterioro cognitivo aparente.")
        elif total >= 21:
            st.warning(f"Puntaje {total}/30 — DETERIORO LEVE: Seguimiento y reevaluacion recomendados.")
        elif total >= 11:
            st.warning(f"Puntaje {total}/30 — DETERIORO MODERADO: Evaluacion especializada necesaria.")
        else:
            st.error(f"Puntaje {total}/30 — DETERIORO GRAVE: Probable demencia avanzada.")

        st.info("Nota: Considerar nivel educativo del paciente al interpretar resultados.")


def escala_rankin():
    st.header("Escala de Rankin Modificada (mRS)")
    st.markdown("""
    > Mide el grado de discapacidad neurologica tras un ACV u otra condicion neurologica.
    > **Escala del 0 al 6**
    """)
    st.divider()

    opciones = {
        "0 - Sin sintomas": 0,
        "1 - Sin discapacidad significativa: realiza todas las actividades habituales": 1,
        "2 - Discapacidad leve: incapaz de algunas actividades previas pero independiente": 2,
        "3 - Discapacidad moderada: requiere ayuda pero camina sin asistencia": 3,
        "4 - Discapacidad moderada-grave: incapaz de caminar y atender necesidades sin ayuda": 4,
        "5 - Discapacidad grave: postrado, incontinente, requiere cuidado constante": 5,
        "6 - Muerte": 6
    }

    seleccion = st.radio("Selecciona el nivel que mejor describe al paciente:", list(opciones.keys()))

    if st.button("Evaluar Rankin"):
        puntaje = opciones[seleccion]
        st.divider()
        st.metric("Escala de Rankin Modificada", puntaje, "/6")
        st.divider()

        if puntaje == 0:
            st.success("Puntaje 0 — RECUPERACION COMPLETA: Sin sintomas.")
        elif puntaje <= 2:
            st.success(f"Puntaje {puntaje} — INDEPENDIENTE: Buen pronostico funcional.")
        elif puntaje <= 4:
            st.warning(f"Puntaje {puntaje} — DEPENDIENTE PARCIAL: Requiere apoyo y rehabilitacion.")
        elif puntaje == 5:
            st.error("Puntaje 5 — DEPENDIENTE TOTAL: Cuidado continuo necesario.")
        else:
            st.error("Puntaje 6 — FALLECIDO.")
