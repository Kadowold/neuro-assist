def aplicar_estilos():
    import streamlit as st
    tema = st.session_state.get("tema", "oscuro")

    if tema == "oscuro":
        bg = "#0f1117"
        card = "#1a1f2e"
        texto = "#ffffff"
        borde = "#2d6a9f"
        btn = "#2d6a9f"
        btn_hover = "#4fc3f7"
        sidebar = "#1a1f2e"
        input_bg = "#1e2736"
    else:
        bg = "#ffffff"
        card = "#ffffff"
        texto = "#1a202c"
        borde = "#3182ce"
        btn = "#3182ce"
        btn_hover = "#2b6cb0"
        sidebar = "#ffffff"
        input_bg = "#ffffff"

    css = f"""
    <style>
        .stApp {{
            background-color: {bg} !important;
            color: {texto} !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar} !important;
            border-right: 2px solid {borde};
        }}
        [data-testid="stSidebar"] * {{
            color: {texto} !important;
        }}
        h1, h2, h3 {{
            color: {borde} !important;
        }}
        p, label, span, div {{
            color: {texto} !important;
        }}
        .stButton > button {{
            background-color: {btn} !important;
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 15px;
            font-weight: bold;
            width: 100%;
        }}
        .stButton > button:hover {{
            background-color: {btn_hover} !important;
        }}
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            background-color: {input_bg} !important;
            color: {texto} !important;
            border: 1px solid {borde} !important;
            border-radius: 6px;
        }}
        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            color: {texto} !important;
        }}
        .stRadio > div {{
            background-color: transparent !important;
        }}
        .stCheckbox > div {{
            background-color: transparent !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {borde} !important;
        }}
        hr {{
            border-color: {borde};
        }}
        .stDataFrame {{
            border: 1px solid {borde};
            border-radius: 8px;
        }}
        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
    </style>
    """
    return css
