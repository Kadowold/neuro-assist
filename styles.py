def aplicar_estilos():
    import streamlit as st
    tema = st.session_state.get("tema", "oscuro")

    if tema == "oscuro":
        bg = "#080c14"
        card = "#111827"
        texto = "#f1f5f9"
        borde = "#2563eb"
        btn = "#2563eb"
        btn_hover = "#60a5fa"
        sidebar = "#0d1117"
        input_bg = "#1e2736"
        accent = "#38bdf8"
    else:
        bg = "#ffffff"
        card = "#f8fafc"
        texto = "#0f172a"
        borde = "#2563eb"
        btn = "#2563eb"
        btn_hover = "#1d4ed8"
        sidebar = "#f1f5f9"
        input_bg = "#ffffff"
        accent = "#2563eb"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {{ font-family: 'Inter', sans-serif !important; }}

        .stApp {{
            background-color: {bg} !important;
            color: {texto} !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar} !important;
            border-right: 1px solid {borde}22;
            padding-top: 20px;
        }}

        [data-testid="stSidebar"] * {{
            color: {texto} !important;
        }}

        h1 {{
            color: {accent} !important;
            font-weight: 700 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.5px;
        }}

        h2 {{
            color: {accent} !important;
            font-weight: 600 !important;
            border-bottom: 2px solid {borde}33;
            padding-bottom: 8px;
        }}

        h3 {{
            color: {texto} !important;
            font-weight: 600 !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, {btn}, {btn_hover}) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px {btn}44 !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px {btn}66 !important;
        }}

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            background-color: {input_bg} !important;
            color: {texto} !important;
            border: 1px solid {borde}44 !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            transition: border 0.2s ease !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border: 1px solid {borde} !important;
            box-shadow: 0 0 0 3px {borde}22 !important;
        }}

        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            color: {texto} !important;
            border: 1px solid {borde}44 !important;
            border-radius: 10px !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {accent} !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: {texto}99 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="metric-container"] {{
            background-color: {card} !important;
            border: 1px solid {borde}22 !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            background-color: {card} !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 4px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {texto}99 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {btn} !important;
            color: white !important;
        }}

        .stDataFrame {{
            border: 1px solid {borde}22 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}

        .stAlert {{
            border-radius: 10px !important;
        }}

        hr {{
            border-color: {borde}22 !important;
            margin: 20px 0 !important;
        }}

        .stSlider > div > div > div {{
            background-color: {btn} !important;
        }}

        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
    </style>
    """
    css += """
    <style>
        @media (max-width: 768px) {
            [data-testid="stSidebar"] {
                transform: none !important;
                width: 100% !important;
                min-width: unset !important;
                position: relative !important;
            }
            [data-testid="stSidebarContent"] {
                padding: 8px !important;
            }
            .main .block-container {
                padding-left: 8px !important;
                padding-right: 8px !important;
            }
        }
    </style>
    """
    return css
