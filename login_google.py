import streamlit as st
from streamlit_oauth import OAuth2Component
import requests

# Datos confidenciales desde Google Cloud Console
CLIENT_ID = "TU_CLIENT_ID"
CLIENT_SECRET = "TU_CLIENT_SECRET"

# Inicializar OAuth2 con Google
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    revoke_endpoint="https://oauth2.googleapis.com/revoke",
)

# Lanzar el botón de login
token = oauth2.authorize_button(
    name="Iniciar sesión con Google",
    redirect_uri="http://localhost:8501",
    scope=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    key="google_login"
)

# Verificar si hay token
if token:
    # Obtener información del usuario usando el access token
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token['access_token']}"}
    ).json()

    email = user_info.get("email", "")
    allowed_emails = ["javierasaavedranazer@gmail.com", "francis.mason@gmail.com"]  
    allowed_domains = ["gmail.com", "tuorganizacion.org"]

    domain = email.split("@")[-1]

    if email in allowed_emails or domain in allowed_domains:
        st.success(f"Bienvenida, {email}")
        st.write("Ya puedes usar el Codificador 3000.")
    else:
        st.error("Acceso denegado. Tu correo no está autorizado.")
else:
    st.info("Por favor, inicia sesión con tu cuenta de Google.")
