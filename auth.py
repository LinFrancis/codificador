import streamlit as st
from streamlit_oauth import OAuth2Component
import requests

# Leer credenciales desde secrets.toml
client_id = st.secrets["oauth"]["client_id"]
client_secret = st.secrets["oauth"]["client_secret"]

# Configurar el componente OAuth2
oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

# Definir el alcance y la URI de redirección
scope = "openid email"
redirect_uri = "https://codificator.streamlit.app/"

# Inicializar variables de sesión si no existen
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Lista de correos autorizados
correos_autorizados = ["francis.mason@gmail.com", "javierasaavedranazer@gmail.com"]

# Botón para cerrar sesión
if st.sidebar.button("Cerrar sesión"):
    st.session_state.token = None
    st.session_state.user_email = None
    st.experimental_rerun()

# Verificar si ya hay sesión válida
if st.session_state.token and st.session_state.user_email:
    st.sidebar.success(f"Sesión activa como {st.session_state.user_email}")
else:
    token = oauth2.authorize_button(
        name="Iniciar sesión con Google",
        redirect_uri=redirect_uri,
        scope=scope,
        key="google_login"
    )

    if token and "access_token" in token and not st.session_state.token:
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token['access_token']}"}
        ).json()

        correo = user_info.get("email")
        if correo in correos_autorizados:
            st.session_state.token = token
            st.session_state.user_email = correo
            st.experimental_set_query_params()  # Limpia los parámetros de la URL
            st.rerun()
        else:
            st.error("Este correo no está autorizado.")
            st.stop()
    elif not token:
        st.warning("Por favor, inicia sesión para continuar.")
        st.stop()
