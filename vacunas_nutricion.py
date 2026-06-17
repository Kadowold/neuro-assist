import streamlit as st

def evaluador_nutricional_ia(db):
    st.subheader("Evaluador Nutricional Pediatrico con IA")
    col1, col2, col3 = st.columns(3)
    with col1:
        edad_meses = st.number_input("Edad del paciente (en meses)", min_value=0, max_value=216, value=24)
    with col2:
        peso = st.number_input("Peso actual (Kg)", min_value=1.0, value=12.0)
    with col3:
        talla = st.number_input("Estatura/Talla (Metros)", min_value=0.3, value=0.85)

    sintomas_conducta = st.multiselect(
        "Indicadores conductuales / Sintomas",
        [
            "Selectividad alimentaria extrema",
            "Perdida drastica de apetito",
            "Obsesion con el peso/figura",
            "Irritabilidad durante las comidas",
            "Regurgitacion frecuente",
            "Letargia o baja energia",
        ],
    )

    if st.button("Analizar Estado Nutricional"):
        imc = peso / (talla ** 2)
        st.metric(label="Indice de Masa Corporal (IMC)", value=f"{imc:.2f}")

        try:
            import anthropic
            api_key = st.secrets["anthropic"]["ANTHROPIC_API_KEY"]
            cliente = anthropic.Anthropic(api_key=api_key)

            prompt = f"""Eres un experto en pediatria y nutricion infantil.
Analiza los siguientes datos de un paciente de {edad_meses} meses de edad:
- IMC calculado: {imc:.2f} (Peso: {peso}kg, Talla: {talla}m)
- Conductas de alarma reportadas: {', '.join(sintomas_conducta) if sintomas_conducta else 'Ninguna'}

Proporciona:
## ESTADO NUTRICIONAL
Clasificacion del IMC para la edad.

## ANALISIS CLINICO
Interpretacion de los datos y conductas reportadas.

## RIESGOS IDENTIFICADOS
Posibles problemas nutricionales o de salud.

## RECOMENDACIONES
Acciones clinicas concretas para el medico.

## SEGUIMIENTO
Frecuencia de control y estudios sugeridos."""

            with st.spinner("IA analizando datos nutricionales..."):
                respuesta = cliente.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(respuesta.content[0].text)

        except Exception as e:
            st.error(f"Error al analizar: {e}")


def calculadora_vacunas():
    st.subheader("Calculadora de Vacunas (Esquema Mexico)")
    edad_meses = st.number_input(
        "Ingresa la edad del menor en meses", min_value=0, max_value=120, value=0
    )

    esquema = [
        (0, ["BCG (Unica)", "Hepatitis B (Nacimiento)"]),
        (2, ["Hexavalente (1ra)", "Rotavirus (1ra)", "Neumococica (1ra)"]),
        (4, ["Hexavalente (2da)", "Rotavirus (2da)", "Neumococica (2da)"]),
        (6, ["Hexavalente (3ra)", "Rotavirus (3ra)", "Influenza (1ra)"]),
        (7, ["Influenza (2da)"]),
        (12, ["SRP Triple Viral (1ra)", "Neumococica (Refuerzo)"]),
        (18, ["Hexavalente (4ta)", "SRP (2da)"]),
        (24, ["Influenza (Anual)"]),
        (36, ["Influenza (Anual)"]),
        (48, ["DPT Triple bacteriana (Refuerzo)", "Influenza (Anual)"]),
        (59, ["Influenza (Anual)"]),
        (72, ["SRP (Refuerzo)"]),
    ]

    aplicadas = []
    pendientes = []
    for meses, vacunas in esquema:
        if edad_meses >= meses:
            aplicadas.extend(vacunas)
        else:
            pendientes.extend(vacunas)

    col1, col2 = st.columns(2)
    with col1:
        st.success("Vacunas que ya deberia tener:")
        for v in aplicadas:
            st.write(f"- {v}")
    with col2:
        st.warning("Proximas vacunas o pendientes:")
        for v in pendientes[:4]:
            st.write(f"- {v}")
