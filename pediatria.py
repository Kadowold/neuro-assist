import streamlit as st
import datetime

def calculadora_dosis(db):
    st.header("Calculadora de Dosis Pediatricas")
    st.markdown("> Calcula dosis segun peso del paciente. Siempre verificar con vademecum actualizado.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="dosis_paciente")
    peso = st.number_input("Peso del paciente (kg)", min_value=0.5, max_value=150.0, value=10.0, step=0.1)

    medicamentos = {
        "Paracetamol": {"dosis": 15, "intervalo": "cada 6-8 horas", "max_dia": 60, "presentación": "Suspensión 160mg/5ml"},
        "Ibuprofeno": {"dosis": 10, "intervalo": "cada 6-8 horas", "max_dia": 40, "presentación": "Suspensión 200mg/5ml"},
        "Amoxicilina": {"dosis": 25, "intervalo": "cada 8 horas", "max_dia": 90, "presentación": "Suspensión 250mg/5ml"},
        "Amoxicilina-Clavulanato": {"dosis": 25, "intervalo": "cada 8 horas", "max_dia": 90, "presentación": "Suspensión 250mg/5ml"},
        "Azitromicina": {"dosis": 10, "intervalo": "una vez al dia por 3 dias", "max_dia": 10, "presentación": "Suspensión 200mg/5ml"},
        "Cetirizina": {"dosis": 0.25, "intervalo": "una vez al dia", "max_dia": 0.5, "presentación": "Jarabe 5mg/5ml"},
        "Salbutamol": {"dosis": 0.1, "intervalo": "cada 4-6 horas", "max_dia": 0.4, "presentación": "Nebulización o inhalador"},
        "Metoclopramida": {"dosis": 0.1, "intervalo": "cada 8 horas", "max_dia": 0.5, "presentación": "Jarabe 5mg/5ml"},
        "Loratadina": {"dosis": 0.2, "intervalo": "una vez al dia", "max_dia": 0.2, "presentación": "Jarabe 5mg/5ml"},
    }

    medicamento = st.selectbox("Medicamento", list(medicamentos.keys()))
    med = medicamentos[medicamento]

    if st.button("Calcular dosis"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            dosis_calculada = peso * med["dosis"]
            dosis_maxima = peso * med["max_dia"]
            col1, col2 = st.columns(2)
            col1.metric("Dosis por toma", f"{dosis_calculada:.1f} mg")
            col2.metric("Dosis maxima diaria", f"{dosis_maxima:.1f} mg")
            st.info(f"Intervalo: {med['intervalo']}")
            st.info(f"Presentacion: {med['presentación']}")
            st.warning("Este calculo es orientativo. Verificar siempre con criterio clinico.")
            try:
                db.collection("dosis").add({
                    "paciente": paciente,
                    "peso": peso,
                    "medicamento": medicamento,
                    "dosis_calculada_mg": round(dosis_calculada, 1),
                    "dosis_maxima_diaria_mg": round(dosis_maxima, 1),
                    "fecha": datetime.datetime.now()
                })
                st.success("Calculo guardado en Firebase.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
def curvas_crecimiento(db):
    st.header("Curvas de Crecimiento OMS")
    st.markdown("> Evalua peso, talla e IMC segun edad y sexo.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="crec_paciente")
    sexo = st.radio("Sexo", ["Masculino", "Femenino"], horizontal=True)
    edad_meses = st.slider("Edad en meses", 0, 60, 12)
    peso = st.number_input("Peso (kg)", min_value=0.5, max_value=30.0, value=10.0, step=0.1)
    talla = st.number_input("Talla (cm)", min_value=40.0, max_value=130.0, value=75.0, step=0.5)

    tablas_niño = {
        0: (2.5, 3.3, 4.4, 46.1, 49.9, 53.7),
        3: (5.0, 6.4, 7.9, 57.3, 61.4, 65.5),
        6: (6.4, 7.9, 9.8, 63.3, 67.6, 71.9),
        9: (7.1, 8.9, 11.0, 68.0, 72.3, 76.9),
        12: (7.7, 9.6, 11.9, 71.7, 75.7, 82.0),
        18: (8.8, 10.9, 13.7, 77.5, 82.3, 88.1),
        24: (9.7, 12.2, 15.3, 82.3, 87.8, 94.0),
        36: (11.2, 14.3, 18.3, 89.0, 96.1, 103.2),
        48: (12.7, 16.3, 21.2, 95.0, 103.3, 111.5),
        60: (14.1, 18.3, 24.2, 100.7, 110.0, 119.2),
    }
    tablas_niña = {
        0: (2.4, 3.2, 4.2, 45.4, 49.1, 52.9),
        3: (4.6, 5.8, 7.4, 55.6, 59.8, 64.0),
        6: (5.8, 7.3, 9.3, 61.2, 65.7, 70.2),
        9: (6.6, 8.2, 10.5, 65.6, 70.1, 75.0),
        12: (7.0, 8.9, 11.5, 69.2, 74.0, 79.2),
        18: (8.1, 10.2, 13.2, 75.0, 80.7, 86.7),
        24: (9.0, 11.5, 14.9, 80.0, 86.4, 93.1),
        36: (10.4, 13.9, 18.1, 86.6, 95.1, 103.1),
        48: (11.8, 16.1, 21.5, 92.9, 102.7, 112.3),
        60: (13.2, 18.2, 24.9, 98.7, 109.4, 120.2),
    }

    tabla = tablas_niño if sexo == "Masculino" else tablas_niña
    edades = sorted(tabla.keys())
    edad_ref = min(edades, key=lambda x: abs(x - edad_meses))
    p3p, p50p, p97p, p3t, p50t, p97t = tabla[edad_ref]
    imc = peso / ((talla / 100) ** 2)

    if st.button("Evaluar crecimiento"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Peso", f"{peso} kg")
            col2.metric("Talla", f"{talla} cm")
            col3.metric("IMC", f"{imc:.1f}")
            st.divider()

            if peso < p3p:
                peso_interp = "Bajo peso severo"
                st.error(f"Peso por debajo del percentil 3 (< {p3p} kg) — Evaluacion nutricional urgente.")
            elif peso <= p97p:
                peso_interp = "Peso adecuado"
                st.success(f"Peso dentro de rango normal ({p3p}-{p97p} kg).")
            else:
                peso_interp = "Posible sobrepeso"
                st.warning(f"Peso por encima del percentil 97 (> {p97p} kg).")

            if talla < p3t:
                talla_interp = "Talla baja"
                st.error(f"Talla por debajo del percentil 3 (< {p3t} cm).")
            elif talla <= p97t:
                talla_interp = "Talla adecuada"
                st.success(f"Talla dentro de rango normal ({p3t}-{p97t} cm).")
            else:
                talla_interp = "Talla alta"
                st.info(f"Talla por encima del percentil 97 (> {p97t} cm).")

            if imc < 14:
                imc_interp = "Desnutrición"
                st.error(f"IMC {imc:.1f} — Desnutrición.")
            elif imc < 18:
                imc_interp = "Normal"
                st.success(f"IMC {imc:.1f} — Normal.")
            elif imc < 25:
                imc_interp = "Sobrepeso"
                st.warning(f"IMC {imc:.1f} — Sobrepeso.")
            else:
                imc_interp = "Obesidad"
                st.error(f"IMC {imc:.1f} — Obesidad.")

            try:
                db.collection("crecimiento").add({
                    "paciente": paciente,
                    "sexo": sexo,
                    "edad_meses": edad_meses,
                    "peso_kg": peso,
                    "talla_cm": talla,
                    "imc": round(imc, 1),
                    "peso_interpretacion": peso_interp,
                    "talla_interpretacion": talla_interp,
                    "imc_interpretacion": imc_interp,
                    "fecha": datetime.datetime.now()
                })
                st.success("Evaluación guardada en Firebase.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")


def desarrollo_infantil(db):
    st.header("Escala de Desarrollo Infantil")
    st.markdown("> Evalua hitos del desarrollo segun edad.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="des_paciente")
    edad = st.selectbox("Edad del niño", [
        "2 meses", "4 meses", "6 meses", "9 meses",
        "12 meses", "18 meses", "24 meses", "3 años", "4 años", "5 años"
    ])

    hitos = {
        "2 meses": ["Levanta cabeza boca abajo", "Sonrie en respuesta a estimulos", "Hace sonidos arrullos", "Sigue objetos con la vista"],
        "4 meses": ["Sostiene cabeza firmemente", "Rie a carcajadas", "Alcanza objetos", "Reconoce cuidadores"],
        "6 meses": ["Se sienta con apoyo", "Se voltea solo", "Pasa objetos de mano en mano", "Responde a su nombre"],
        "9 meses": ["Se sienta sin apoyo", "Gatea", "Pinza inferior", "Ansiedad ante extranios"],
        "12 meses": ["Se pone de pie solo", "Camina con apoyo", "Dice 1-3 palabras con significado", "Imita gestos"],
        "18 meses": ["Camina solo bien", "Dice 10-20 palabras", "Garabatea", "Juego simbolico simple"],
        "24 meses": ["Corre", "Frases de 2 palabras", "Apila 6 cubos", "Imita tareas del hogar"],
        "3 anos": ["Salta en un pie", "Frases de 3-4 palabras", "Dibuja circulo", "Juego cooperativo simple"],
        "4 anos": ["Salta varios pasos", "Cuenta historias", "Dibuja persona con 3 partes", "Distingue fantasia de realidad"],
        "5 anos": ["Salta la cuerda", "Habla claramente", "Escribe algunas letras", "Sigue reglas de juego"],
    }

    lista_hitos = hitos[edad]
    hitos_cumplidos = 0

    for hito in lista_hitos:
        if st.checkbox(hito, key=f"hito_{edad}_{hito}"):
            hitos_cumplidos += 1

    if st.button("Evaluar desarrollo"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            total = len(lista_hitos)
            porcentaje = (hitos_cumplidos / total) * 100
            col1, col2 = st.columns(2)
            col1.metric("Hitos cumplidos", f"{hitos_cumplidos}/{total}")
            col2.metric("Porcentaje", f"{porcentaje:.0f}%")
            st.divider()

            if porcentaje >= 80:
                interpretación = "Desarrollo adecuado para la edad."
                st.success(interpretación)
            elif porcentaje >= 60:
                interpretación = "Algunos retrasos. Seguimiento en 3 meses."
                st.warning(interpretación)
            else:
                interpretación = "Retraso significativo. Evaluación especializada urgente."
                st.error(interpretación)

            try:
                db.collection("desarrollo").add({
                    "paciente": paciente,
                    "edad": edad,
                    "hitos_cumplidos": hitos_cumplidos,
                    "total_hitos": total,
                    "porcentaje": round(porcentaje, 1),
                    "interpretacion": interpretación,
                    "fecha": datetime.datetime.now()
                })
                st.success("Evaluacion guardada en Firebase.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")


def triaje_pediatrico(db):
    st.header("Triaje Pediatrico")
    st.markdown("> Detecta signos de alarma y determina urgencia de atención.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="triaje_paciente")
    edad_meses = st.number_input("Edad en meses", min_value=0, max_value=216, value=12)
    peso = st.number_input("Peso (kg)", min_value=0.5, max_value=100.0, value=10.0, step=0.1)

    st.subheader("Signos vitales")
    col1, col2, col3 = st.columns(3)
    with col1:
        fr = st.number_input("Frec. respiratoria (rpm)", min_value=0, max_value=100, value=30)
    with col2:
        fc = st.number_input("Frec. cardiaca (lpm)", min_value=0, max_value=300, value=100)
    with col3:
        temp = st.number_input("Temperatura (C)", min_value=34.0, max_value=42.0, value=37.0, step=0.1)

    sato2 = st.slider("Saturación de O2 (%)", 70, 100, 98)

    st.subheader("Signos de alarma presentes")
    alarmas_lista = [
        "No responde o respuesta minima",
        "Dificultad respiratoria severa",
        "Cianosis",
        "Convulsión activa o reciente",
        "Fontanela abombada",
        "Petequias o purpura generalizada",
        "Llanto inconsolable mas de 2 horas",
        "Rechazo total del alimento en menor de 3 meses",
        "Vomitos en proyectil repetidos",
        "Deshidratación severa",
        "Fiebre en menor de 3 meses",
        "Rigidez de nuca",
    ]

    alarmas_presentes = []
    for signo in alarmas_lista:
        if st.checkbox(signo, key=f"alarma_{signo}"):
            alarmas_presentes.append(signo)

    if st.button("Evaluar triaje"):
        if paciente == "":
            st.warning("Por favor ingresa el nombre del paciente.")
        else:
            puntos = 0
            alertas = []

            if edad_meses < 2 and fr > 60:
                puntos += 2
                alertas.append("FR elevada para menor de 2 meses")
            elif edad_meses < 12 and fr > 50:
                puntos += 2
                alertas.append("FR elevada para lactante")
            elif edad_meses < 60 and fr > 40:
                puntos += 1
                alertas.append("FR elevada para preescolar")

            if fc > 180 or fc < 60:
                puntos += 2
                alertas.append("FC fuera de rango critico")
            elif fc > 150:
                puntos += 1
                alertas.append("Taquicardia moderada")

            if temp >= 38.0 and edad_meses < 3:
                puntos += 3
                alertas.append("Fiebre en menor de 3 meses")
            elif temp >= 39.5:
                puntos += 1
                alertas.append("Fiebre alta")

            if sato2 < 90:
                puntos += 3
                alertas.append("Saturación critica < 90%")
            elif sato2 < 94:
                puntos += 2
                alertas.append("Saturación baja < 94%")

            puntos += len(alarmas_presentes) * 2

            st.divider()
            if alertas or alarmas_presentes:
                st.markdown("**Alertas detectadas:**")
                for a in alertas + alarmas_presentes:
                    st.markdown(f"- {a}")
            st.divider()

            if puntos >= 6:
                nivel = "ROJO - EMERGENCIA"
                interpretacion = "Atención inmediata. Riesgo vital."
                st.error(f"{nivel}: {interpretación}")
            elif puntos >= 3:
                nivel = "NARANJA - URGENCIA"
                interpretación = "Atención en menos de 30 minutos."
                st.warning(f"{nivel}: {interpretación}")
            elif puntos >= 1:
                nivel = "AMARILLO - SEMI-URGENCIA"
                interpretación = "Atención en menos de 2 horas."
                st.warning(f"{nivel}: {interpretación}")
            else:
                nivel = "VERDE - NO URGENTE"
                interpretación = "Puede esperar atención programada."
                st.success(f"{nivel}: {interpretación}")

            try:
                db.collection("triaje").add({
                    "paciente": paciente,
                    "edad_meses": int(edad_meses),
                    "peso_kg": peso,
                    "fr": int(fr),
                    "fc": int(fc),
                    "temperatura": temp,
                    "sato2": int(sato2),
                    "nivel_triaje": nivel,
                    "interpretación": interpretacion,
                    "alarmas_presentes": alarmas_presentes,
                    "fecha": datetime.datetime.now()
                })
                st.success("Triaje guardado en Firebase.")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
