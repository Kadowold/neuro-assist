def aplicar_estilos():
    import streamlit as st
    tema = st.session_state.get("tema", "oscuro")

    if tema == "oscuro":
        bg =          "#020818"
        bg2 =         "#0a1628"
        card =        "#0d1f3c"
        card2 =       "#112244"
        texto =       "#e8f0fe"
        subtexto =    "#8ba3cc"
        borde =       "#1e3a6e"
        accent =      "#c9a84c"
        accent2 =     "#f0c96e"
        btn =         "#1a3a6e"
        btn2 =        "#c9a84c"
        sidebar =     "#070f1e"
        input_bg =    "#0d1f3c"
        success =     "#0d4a2e"
        warning =     "#4a3200"
        error =       "#4a0d0d"
    else:
        bg =          "#f0f4ff"
        bg2 =         "#e8eeff"
        card =        "#ffffff"
        card2 =       "#f8faff"
        texto =       "#0a1628"
        subtexto =    "#4a6080"
        borde =       "#c0d0f0"
        accent =      "#b8860b"
        accent2 =     "#d4a017"
        btn =         "#1a3a6e"
        btn2 =        "#c9a84c"
        sidebar =     "#e8eeff"
        input_bg =    "#ffffff"
        success =     "#e8f5ee"
        warning =     "#fff8e8"
        error =       "#fff0f0"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

        * {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* ── Fondo principal ── */
        .stApp {{
            background: linear-gradient(135deg, {bg} 0%, {bg2} 100%) !important;
            color: {texto} !important;
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {sidebar} 0%, {bg2} 100%) !important;
            border-right: 1px solid {accent}33 !important;
        }}

        [data-testid="stSidebar"] * {{
            color: {texto} !important;
        }}

        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: {card} !important;
            border: 1px solid {accent}44 !important;
            border-radius: 10px !important;
        }}

        /* ── Titulos ── */
        h1 {{
            font-family: 'Playfair Display', serif !important;
            color: {accent2} !important;
            font-weight: 700 !important;
            font-size: 2.4rem !important;
            letter-spacing: -0.5px !important;
            text-shadow: 0 2px 20px {accent}44 !important;
        }}

        h2 {{
            color: {accent} !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
            border-bottom: 1px solid {accent}33 !important;
            padding-bottom: 8px !important;
        }}

        h3 {{
            color: {texto} !important;
            font-weight: 600 !important;
        }}

        /* ── Botones principales ── */
        .stButton > button {{
            background: linear-gradient(135deg, {btn} 0%, #0f2a52 100%) !important;
            color: {accent2} !important;
            border: 1px solid {accent}66 !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            width: 100% !important;
            letter-spacing: 0.3px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3), inset 0 1px 0 {accent}22 !important;
        }}

        .stButton > button:hover {{
            background: linear-gradient(135deg, {btn2} 0%, {accent} 100%) !important;
            color: {bg} !important;
            border-color: {accent2} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px {accent}44 !important;
        }}

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            background-color: {input_bg} !important;
            color: {texto} !important;
            border: 1px solid {borde} !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            transition: all 0.2s ease !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px {accent}22 !important;
        }}

        /* ── Selectbox ── */
        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            color: {texto} !important;
            border: 1px solid {borde} !important;
            border-radius: 10px !important;
        }}

        /* ── Metricas ── */
        [data-testid="metric-container"] {{
            background: linear-gradient(135deg, {card} 0%, {card2} 100%) !important;
            border: 1px solid {accent}33 !important;
            border-radius: 14px !important;
            padding: 20px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2), inset 0 1px 0 {accent}11 !important;
            transition: transform 0.2s ease !important;
        }}

        [data-testid="metric-container"]:hover {{
            transform: translateY(-2px) !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {accent2} !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: {subtexto} !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{
            background: {card} !important;
            border-radius: 12px !important;
            padding: 6px !important;
            border: 1px solid {borde} !important;
            gap: 4px !important;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            color: {subtexto} !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {btn} 0%, #0f2a52 100%) !important;
            color: {accent2} !important;
            border: 1px solid {accent}44 !important;
        }}

        /* ── Dataframe ── */
        .stDataFrame {{
            border: 1px solid {accent}22 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}

        /* ── Alertas ── */
        .stSuccess > div {{
            background: {success} !important;
            border-left: 4px solid #2ecc71 !important;
            border-radius: 10px !important;
        }}

        .stWarning > div {{
            background: {warning} !important;
            border-left: 4px solid {accent} !important;
            border-radius: 10px !important;
        }}

        .stError > div {{
            background: {error} !important;
            border-left: 4px solid #e63946 !important;
            border-radius: 10px !important;
        }}

        .stInfo > div {{
            background: {card} !important;
            border-left: 4px solid #4fc3f7 !important;
            border-radius: 10px !important;
        }}

        /* ── Slider ── */
        .stSlider > div > div > div > div {{
            background: linear-gradient(90deg, {btn} 0%, {accent} 100%) !important;
        }}

        /* ── Radio y checkbox ── */
        .stRadio > div, .stCheckbox > div {{
            background: transparent !important;
        }}

        /* ── Divisor ── */
        hr {{
            border: none !important;
            border-top: 1px solid {accent}22 !important;
            margin: 20px 0 !important;
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: {bg};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {accent}66;
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {accent};
        }}

        /* ── Ocultar elementos de Streamlit ── */
        footer {{ visibility: hidden !important; }}
        #MainMenu {{ visibility: hidden !important; }}
        header {{ visibility: hidden !important; }}

    </style>
    """
    return css
