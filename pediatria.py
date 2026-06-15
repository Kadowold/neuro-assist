import streamlit as st
import datetime

def calculadora_dosis(db):
    st.header("Calculadora de Dosis Pediatricas")
    st.markdown("> Calcula dosis segun peso del paciente. Siempre verificar con vademecum actualizado.")
    st.divider()

    paciente = st.text_input("Nombre del paciente", key="dosis_paciente")
    peso = st.number_input("Peso del paciente (kg)", min_value=0.5, max_value=150.0, value=10.0, step=0.1)

    medicamentos = {
        "Paracetamol": {"dosis": 15, "intervalo": "cada 6-8 horas", "max_dia": 60, "presentacion": "Suspension 160mg/5ml"},
        "Ibuprofeno": {"dosis": 10, "intervalo": "cada 6-8 horas", "max_dia": 40, "presentacion": "Suspension 200mg/5ml"},
        "Amoxicilina": {"dosis": 25, "intervalo": "cada 8 horas", "max_dia": 90, "presentacion": "Suspension 250mg/5ml"},
        "Amoxicilina-Clavulanato": {"dosis": 25, "intervalo": "cada 8 horas", "max_dia": 90, "presentacion": "Suspension 250mg/5ml"},
        "Azitromicina": {"dosis": 10, "intervalo": "una vez al dia por 3 dias", "max_dia": 10, "presentacion": "Suspension 200mg/5ml"},
        "Cetirizina": {"dosis": 0.25, "intervalo": "una vez al dia", "max_dia": 0.5, "presentacion": "Jarabe 5mg/5ml"},
        "Salbutamol": {"dosis": 0.1, "intervalo": "cada 4-6 horas", "max_dia": 0.4, "presentacion": "Nebulizacion o inhalador"},
        "Metoclopramida": {"dosis": 0.1, "intervalo": "cada 8 horas", "max_dia": 0.5, "presentacion": "Jarabe 5mg/5ml"},
        "Loratadina": {"dosis": 0.2, "intervalo": "una vez al dia", "max_dia": 0.2, "presentacion": "Jarabe 5mg/5ml"},
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
            st.info(f"Presentacion: {med['presentacion']}")
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
