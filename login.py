import streamlit as st
import bcrypt
from datetime import datetime


# ---------- Utilidades de contraseña ----------

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


# ---------- Acceso a Firestore ----------

def obtener_usuario(db, usuario):
    usuario_id = usuario.strip().lower()
    doc = db.collection("usuarios").document(usuario_id).get()
    if doc.exists:
        return doc.to_dict()
    return None


def crear_usuario(db, usuario, password, nombre_completo=""):
    usuario_id = usuario.strip().lower()
    db.collection("usuarios").document(usuario_id).set({
        "usuario": usuario.strip(),
        "password_hash": hash_password(password),
        "nombre_completo": nombre_completo.strip(),
        "creado_el": datetime.now(),
    })


# ---------- UI ----------

def mostrar_login(db):
    if "tema" not in st.session_state:
        st.session_state.tema = "oscuro"

    col_tema = st.columns([6, 1])[1]
    with col_tema:
        if st.button("🌙" if st.session_state.tema == "claro" else "☀️"):
            st.session_state.tema = "claro" if st.session_state.tema == "oscuro" else "oscuro"
            st.rerun()

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
            margin: 40px auto 20px auto;
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
            margin-bottom: 8px;
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

    tab_login, tab_registro = st.tabs(["Iniciar sesion", "Crear cuenta"])

    with tab_login:
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submitted = st.form_submit_button("Iniciar sesion")

            if submitted:
                if not usuario or not password:
                    st.error("Completa usuario y contraseña.")
                else:
                    datos = obtener_usuario(db, usuario)
                    if datos and verificar_password(password, datos["password_hash"]):
                        st.session_state.autenticado = True
                        st.session_state.usuario = datos.get("usuario", usuario)
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

    with tab_registro:
        with st.form("registro_form"):
            nuevo_usuario = st.text_input("Elige un usuario", placeholder="Minimo 3 caracteres")
            nombre_completo = st.text_input("Nombre completo (opcional)")
            nueva_password = st.text_input("Contraseña", type="password", placeholder="Minimo 6 caracteres")
            confirmar_password = st.text_input("Confirma tu contraseña", type="password")
            submitted_reg = st.form_submit_button("Crear cuenta")

            if submitted_reg:
                if len(nuevo_usuario.strip()) < 3:
                    st.error("El usuario debe tener al menos 3 caracteres.")
                elif len(nueva_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                elif nueva_password != confirmar_password:
                    st.error("Las contraseñas no coinciden.")
                elif obtener_usuario(db, nuevo_usuario) is not None:
                    st.error("Ese usuario ya existe. Elige otro.")
                else:
                    crear_usuario(db, nuevo_usuario, nueva_password, nombre_completo)
                    st.success("Cuenta creada. Ya puedes iniciar sesion en la pestana de al lado.")


def mostrar_logout():
    with st.sidebar:
        st.divider()
        st.markdown(f"👤 **{st.session_state.usuario}**")
        if st.button("Cerrar sesion"):
            st.session_state.autenticado = False
            st.session_state.usuario = ""
            st.rerun()
