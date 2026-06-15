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
    else:
        bg = "#f0f4f8"
        card = "#ffffff"
        texto = "#1a202c"
        borde = "#3182ce"
        btn = "#3182ce"
        btn_hover = "#2b6cb0"
        sidebar = "#e2e8f0"

    css = f"""
    <style>
        .stApp {{ background-color: {bg}; color: {texto}; }}
        [data-testid="stSidebar"] {{
            background-color: {sidebar};
            border-right: 2px solid {borde};
        }}
        h1, h2, h3 {{ color: {borde} !important; }}
        .stButton > button {{
            background-color: {btn};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 15px;
            font-weight: bold;
            width: 100%;
        }}
        .stButton > button:hover {{
            background-color: {btn_hover};
            color: {bg};
        }}
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: {card};
            color: {texto};
            border: 1px solid {borde};
            border-radius: 6px;
        }}
        .stSelectbox > div > div {{
            background-color: {card};
            color: {texto};
        }}
        hr {{ border-color: {borde}; }}
        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
    </style>
    """
    return css
