def aplicar_estilos():
    css = """
    <style>
        .stApp {
            background-color: #0f1117;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1f2e;
            border-right: 2px solid #2d6a9f;
        }
        h1 {
            color: #4fc3f7 !important;
        }
        h2, h3 {
            color: #81d4fa !important;
        }
        .stButton > button {
            background-color: #2d6a9f;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 15px;
            font-weight: bold;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #4fc3f7;
            color: #0f1117;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #1e2736;
            color: white;
            border: 1px solid #2d6a9f;
            border-radius: 6px;
        }
        .stSelectbox > div > div {
            background-color: #1e2736;
            color: white;
        }
        hr {
            border-color: #2d6a9f;
        }
    </style>
    """
    return css