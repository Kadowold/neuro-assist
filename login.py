import streamlit as st
import hashlib

# Usuarios permitidos: {"usuario": "contrasena_hasheada"}
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

USUARIOS = {
    "Alexiis": hash_password("carlos2026"),
    "Montserrath": hash_password("Montse_23"),
}

def mostrar_login():
    # Modo oscuro/claro
    if "tema" not in st.session_state:
        st.session_state.tema = "oscuro"

    col_tema = st.columns([6, 1])[1]
    with col_tema:
        if st.button("🌙" if st.session_state.tema == "claro" else "☀️"):
            st.session_state.tema = "claro" if st.session_state.tema == "oscuro" else "oscuro"
            st.rerun()

    # Colores segun tema
    if st.session_state.tema == "oscuro":
        bg = "#0f1117"
        card = "#1a1f2e"
        texto = "#ffffff"
        subtexto = "#8892a4"
        borde = "#2d6a9f"
        btn = "#2d6a9f"
        btn_hover = "#4fc3f7"
    else:
        bg = "#f0f4f8"
        card = "#ffffff"
        texto = "#1a202c"
        subtexto = "#4a5568"
        borde = "#3182ce"
        btn = "#3182ce"
        btn_hover = "#2b6cb0"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg}; }}
        .login-card {{
            background-color: {card};
            border: 1px solid {borde};
            border-radius: 16px;
            padding: 40px;
            max-width: 420px;
            margin: 60px auto;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        .login-title {{
            color: {texto};
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 4px;
        }}
        .login-sub {{
            color: {subtexto};
            font-size: 14px;
            text-align: center;
            margin-bottom: 32px;
        }}
        .stTextInput > div > div > input {{
            background-color: {bg};
            color: {texto};
            border: 1px solid {borde};
            border-radius: 8px;
            padding: 10px 14px;
        }}
        .stButton > button {{
            background-color: {btn};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 15px;
            font-weight: 600;
            width: 100%;
            margin-top: 8px;
        }}
        .stButton > button:hover {{
            background-color: {btn_hover};
        }}
        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="login-card">
        <div class="login-title">🧠 NeuroApp</div>
        <div class="login-sub">Sistema medico de seguimiento neurologico</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("Contrasena", type="password", placeholder="Ingresa tu contrasena")
        submitted = st.form_submit_button("Iniciar sesion")

        if submitted:
            if usuario in USUARIOS and USUARIOS[usuario] == hash_password(password):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuario o contrasena incorrectos.")

def mostrar_logout():
    with st.sidebar:
        st.divider()
        st.markdown(f"👤 **{st.session_state.usuario}**")
        if st.button("Cerrar sesion"):
            st.session_state.autenticado = False
            st.session_state.usuario = ""
            st.rerun()
