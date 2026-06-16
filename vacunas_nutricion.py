import streamlit as st
import openai 


def evaluador_nutricional_ia(db=None): 
    st.subheader("👶 Evaluador Nutricional Pediátrico con IA")

    col1, col2, col3 = st.columns(3)
    with col1:
        edad_meses = st.number_input(
            "Edad del paciente (en meses)", min_value=0, max_value=216, value=24
        )
    with col2:
        peso = st.number_input("Peso actual (Kg)", min_value=1.0, value=12.0)
    with col3:
        talla = st.number_input(
            "Estatura/Talla (Metros)", min_value=0.3, value=0.85
        )

    sintomas_conducta = st.multiselect(
        "Indicadores conductuales / Síntomas",
        [
            "Selectividad alimentaria extrema",
            "Pérdida drástica de apetito",
            "Obsesión con el peso/figura",
            "Irritabilidad durante las comidas",
            "Regurgitación frecuente",
            "Letargia o baja energía",
        ],
    )

    if st.button("Analizar Estado Nutricional"):
        # Cálculo de IMC básico
        imc = peso / (talla**2)
        st.metric(label="Índice de Masa Corporal (IMC)", value=f"{imc:.2f}")

        client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])

        prompt = f"""
        Actúa como un experto en pediatría y nutrición. Analiza los siguientes datos de un paciente de {edad_meses} meses de edad:
        - IMC calculado: {imc:.2f} (Peso: {peso}kg, Talla: {talla}m)
        - Conductas de alarma reportadas: {', '.join(sintomas_conducta) if sintomas_conducta else 'Ninguna'}.
        Proporciona un análisis breve, posibles percentiles estimados de riesgo y recomendaciones clínicas orientadas a la salud mental y física del menor.
        """

        with st.spinner("IA analizando datos nutricionales..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            st.info(response.choices[0].message.content)


def calculadora_vacunas():
    st.subheader("💉 Calculadora de Vacunas (Esquema México)")
    edad_meses = st.number_input(
        "Ingresa la edad del menor en meses", min_value=0, max_value=120, value=0
    )

    # Base de datos del esquema de vacunación mexicano
    esquema = [
        (0, ["BCG (Única)", "Hepatitis B (Nacimiento)"]),
        (2, ["Hexavalente (1ra)", "Rotavirus (1ra)", "Neumocócica (1ra)"]),
        (4, ["Hexavalente (2da)", "Rotavirus (2da)", "Neumocócica (2da)"]),
        (6, ["Hexavalente (3ra)", "Rotavirus (3ra)", "Influenza (1ra)"]),
        (7, ["Influenza (2da)"]),
        (12, ["SRP / Triple Viral (1ra)", "Neumocócica (Refuerzo)"]),
        (18, ["Hexavalente (4ta)", "SRP (2da en nuevos esquemas)"]),
        (24, ["Influenza (Anual)"]),
        (36, ["Influenza (Anual)"]),
        (48, ["DPT / Triple bacteriana (Refuerzo)", "Influenza (Anual)"]),
        (59, ["Influenza (Anual)"]),
        (72, ["SRP (Refuerzo tradicional)"]),
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
        st.success("✅ Vacunas que ya debería tener:")
        for v in aplicadas:
            st.write(f"- {v}")
    with col2:
        st.warning("⏳ Próximas vacunas o pendientes:")
        for v in pendientes[:4]:  # Muestra las próximas más relevantes
            st.write(f"- {v}")
