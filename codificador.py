import streamlit as st
import pandas as pd
import datetime
import csv
import os
from rapidfuzz import fuzz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random


from PIL import Image


# === Set page config early ===
st.set_page_config(
    page_title="Codificator 3002 - Dra. Javiera Saavedra Nazer",
    layout="wide",
    initial_sidebar_state="expanded"
)



# --- Autenticación básica con usuario y contraseña desde secrets.toml ---
def verificar_credenciales(usuario_input, contrasena_input):
    usuario_valido = st.secrets["oauth"]["username"]
    contrasena_valida = st.secrets["oauth"]["password"]

    return usuario_input == usuario_valido and contrasena_input == contrasena_valida

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    with st.form("login_form"):
        st.markdown("## Iniciar sesión")
        usuario_input = st.text_input("Usuario")
        contrasena_input = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if verificar_credenciales(usuario_input, contrasena_input):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales inválidas. Intenta nuevamente.")
    st.stop()

with st.sidebar:
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()









st.markdown("""
<style>
/* Force white background for main content and sidebar */
body, .main, .stApp {
    background-color: white !important;
    color: black !important;
}

/* Optional: ensure headers stay visible on white */
h1, h2, h3, h4, h5, h6, p, label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

frases_buda = [
    "El odio no cesa con el odio, sino con el amor. – Dhammapada, verso 5",
    "La mente lo es todo. En lo que piensas, te conviertes. – Dhammapada, verso 1",
    "Más vale conquistarse a uno mismo que ganar mil batallas. – Dhammapada, verso 103",
    "No hay fuego como la pasión, ni cadena como el odio. – Dhammapada, verso 251",
    "Ni siquiera un dios puede cambiar el pasado. – Anguttara Nikaya 5.57",
    "El insensato duerme como si ya estuviera muerto, pero el sabio está despierto y vive con atención. – Dhammapada, verso 21",
    "Así como una roca sólida no se mueve con el viento, el sabio permanece impasible ante la alabanza y la culpa. – Dhammapada, verso 81",
    "No habites en el pasado, no sueñes con el futuro, concentra la mente en el momento presente. – Majjhima Nikaya 131",
    "Una mente disciplinada trae felicidad. – Dhammapada, verso 35",
    "Así como una flor hermosa pero sin fragancia, así son las palabras sin acción. – Dhammapada, verso 51",
    "Quien observa su mente con atención, encuentra libertad. – Satipatthana Sutta",
    "La raíz del sufrimiento es el apego. – Samyutta Nikaya 56.11",
    "Todo lo que tiene un comienzo tiene un final. – Majjhima Nikaya 131",
    "El dolor es inevitable, pero el sufrimiento es opcional. – Sutta Nipāta 4.16",
    "Lo que piensas, lo serás. Lo que sientas, lo atraerás. Lo que imagines, lo crearás. – Dhammapada, resumen",
    "Deja de lado lo que no es útil. – Majjhima Nikaya 22",
    "El sabio no se apega a lo que ve ni a lo que oye. – Sutta Nipāta 4.3",
    "El que envidia no encontrará la paz del corazón. – Dhammapada, verso 290",
    "No dañes a los demás con lo que te causa dolor a ti mismo. – Udana 5.18",
    "Cuando uno se libera del odio, despierta. – Dhammapada, verso 87",
    "Todo es efímero. – Dhammapada, verso 277",
    "Dominarse a sí mismo es una victoria mayor que conquistar a otros. – Dhammapada, verso 103",
    "Las palabras tienen el poder de destruir y sanar. – Sutta Nipāta 3.9",
    "El camino no está en el cielo, el camino está en el corazón. – Dhammapada, verso 183",
    "La paz viene de dentro. No la busques fuera. – Majjhima Nikaya 131",
    "Un pensamiento impuro arruina todo. – Dhammapada, verso 42",
    "La sabiduría es la mejor guía. – Anguttara Nikaya 3.65",
    "Sé una luz para ti mismo. – Mahaparinibbana Sutta",
    "La ignorancia es la peor forma de oscuridad. – Samyutta Nikaya 35.191",
    "La mente es difícil de dominar, pero se puede entrenar. – Dhammapada, verso 35",
    "No hay mayor riqueza que el contentamiento. – Dhammapada, verso 204",
    "La compasión es el lenguaje del corazón. – Sutta Nipāta 1.8",
    "No creas nada simplemente porque lo diga una tradición. – Kalama Sutta",
    "Quien se ama a sí mismo, no daña a los demás. – Udana 5.1",
    "El cuerpo es frágil, como una vasija de barro. – Dhammapada, verso 40",
    "La sabiduría nace del silencio. – Sutta Nipāta 2.12",
    "Nada es permanente. – Dhammapada, verso 277",
    "La verdadera libertad es interior. – Majjhima Nikaya 140",
    "Mejor una palabra que apacigüe que mil sin sentido. – Dhammapada, verso 100",
    "Donde hay amor, no hay miedo. – Sutta Nipāta 2.13",
    "El camino es el noble óctuple sendero. – Dhammapada, verso 191",
    "No te aferres a nada, todo cambia. – Samyutta Nikaya 22.59",
    "El sabio reconoce la transitoriedad de todo. – Dhammapada, verso 277",
    "El que practica la verdad vive feliz. – Dhammapada, verso 24",
    "Conquistar el ego es la verdadera victoria. – Dhammapada, verso 233",
    "La vida es preciosa. No la desperdicies. – Sutta Nipāta 1.1",
    "El deseo es la raíz de todo sufrimiento. – Samyutta Nikaya 56.11",
    "La pureza y la impureza dependen de uno mismo. – Dhammapada, verso 165",
    "Quien camina con sabiduría no teme a la muerte. – Dhammapada, verso 128",
    "Todo ser teme el castigo. Comparte esa comprensión. – Dhammapada, verso 129",
    "La serenidad es la mayor bendición. – Sutta Nipāta 2.4",
    "La meditación trae claridad. – Dhammapada, verso 282",
    "No acumules lo que no necesitas. – Majjhima Nikaya 22",
    "Quien se libera del deseo encuentra la paz. – Samyutta Nikaya 35.28",
    "No hay felicidad superior a la paz interior. – Dhammapada, verso 203",
    "El sabio vive en armonía consigo mismo. – Dhammapada, verso 95",
    "El cuerpo se desgasta, pero la mente puede florecer. – Dhammapada, verso 146",
    "Quien actúa con rectitud es invulnerable. – Dhammapada, verso 39",
    "La amabilidad es una joya que nunca se pierde. – Sutta Nipāta 1.8",
    "Solo tú puedes recorrer tu camino. – Dhammapada, verso 276",
    "El necio duerme sin rumbo, el sabio se cultiva. – Dhammapada, verso 20",
    "La verdad no necesita defensa. – Majjhima Nikaya 58",
    "El sabio no discute por necedad. – Dhammapada, verso 6",
    "No seas esclavo del placer, ni del dolor. – Sutta Nipāta 2.13",
    "Es mejor vivir solo que en mala compañía. – Dhammapada, verso 330",
    "El sabio evita la compañía de necios. – Dhammapada, verso 61",
    "Nada puede esconderse por mucho tiempo: el sol, la luna y la verdad. – Dhammapada, verso 128",
    "Haz el bien, evita el mal, y purifica tu mente. – Dhammapada, verso 183",
    "Cuando el sabio habla, el mundo escucha. – Sutta Nipāta 3.2",
    "La belleza externa no es nada sin la belleza del alma. – Dhammapada, verso 147",
    "El que se autoconoce es invencible. – Dhammapada, verso 160",
    "La vida bien vivida es breve pero valiosa. – Dhammapada, verso 110",
    "No te lamentes por lo que ya pasó. – Samyutta Nikaya 22.59",
    "La luz de una vela puede encender miles sin apagarse. – Sutta Nipāta 2.2"
]



# Mostrar una frase aleatoria como caption
st.caption(random.choice(frases_buda))

# Lista de nombres de archivos (sin extensión)
logos_codificator_list = [
    "codificator_hello_kitty_minina",
    "codificator_hello_kitty_minina_02",
    "codificator_hello_kitty_minina_03",
    "codificator_kuromi",
    "codificator_kuromi_02",
    "codificator_kuromi_03",
    "codificator_kuromi_04",
    "codificator_kuromi_05",
    "codificator_kuromi_06",
    "codificator_kuromi_07",
    "logo_codificator",
    "logo_codificator_2",
    "codificator_hangyodon_01",
    "ChatGPT Image May 19, 2025, 12_25_50 AM",
    "ChatGPT Image May 19, 2025, 12_29_33 AM,
]

# Elegir un archivo al azar
selected_logo = random.choice(logos_codificator_list)

# Construir la ruta al archivo
logo_path = f"image/{selected_logo}.png"

# Mostrar el logo aleatorio
st.logo(logo_path, size="large", link=None, icon_image=logo_path)




def connect_to_gsheet(spreadsheet_name, sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = st.secrets["gsheets"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
    client = gspread.authorize(credentials)
  
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)

# Sheet name variables
SPREADSHEET_NAME = 'DIAGNOSIS_DATABASE'
SHEET_NAME = 'DIAGNOSIS'

# Connect to the Sheet
sheet_by_name = connect_to_gsheet(SPREADSHEET_NAME, SHEET_NAME)


# =========================
# SHEET FUNCTIONS
# =========================
def read_data():
    data = sheet_by_name.get_all_records()  
    return pd.DataFrame(data)

df_glosary = read_data()






# Cargar fuente Montserrat para un diseño moderno
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# Inyectar CSS personalizado para mejorar el estilo.
st.markdown(
    """
    <style>
    /* Estilos globales */
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: white;
        color: black;
    }
    
    /* Contenedor con degradado para el título */
    .title-container {
        background: linear-gradient(135deg, #B7B1F2 0%, #FDB7EA 100%);
        padding: 20px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    /* Estilo del texto del título */
    .title-text {
        font-size: 48px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    /* Tarjeta personalizada para resultados */
    .card {
        padding: 15px; 
        background-color: white;
        border-left: 6px solid #FDB7EA; 
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        color: #B7B1F2;
    }
    .card-text {
        font-size: 20px;
        margin-top: 10px;
        color: black;
    }
    .card-footer {
        font-size: 14px;
        margin-top: 10px;
        color: black;
    }
    
    /* Encabezado de la barra lateral */
    .sidebar-header {
        color: #B7B1F2;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Layout in columns (image on left, welcome box on right)
col1, col2 = st.columns([1, 3])



with col1:
    st.image(logo_path, width=200)

with col2:
    st.markdown("""
    <style>
    .hello-box {
        background: linear-gradient(to bottom, #fff6fb, #ffeef7);
        padding: 24px;
        border-radius: 18px;
        border: 2px solid #ffb6d5;
        box-shadow: 0px 4px 12px rgba(255, 182, 213, 0.3);
        font-family: 'Segoe UI', sans-serif;
        color: #a64d79;
        margin-bottom: 2rem;
    }
    .hello-box h2 {
        color: #ff69b4;
        font-size: 24px;
        margin-bottom: 12px;
        text-align: center;
    }
    .hello-box p {
        font-size: 16px;
        margin: 8px 0;
    }
    .hello-box a {
        color: #6699cc;
        text-decoration: none;
        font-weight: bold;
    }
        </style>

    <div class="hello-box">
        <h2>Bienvenida Dra. Javiera Saavedra Nazer</h2>
        <p>🔍 Use la <strong>barra lateral</strong> para filtrar por fuente o grupo e ingresar palabras clave.</p>
        <p>📝 En el menú <strong>"Editor"</strong> puede agregar, editar o eliminar información de la base de datos. Los cambios se actualizan en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)





# Inicializar el historial de búsqueda en la sesión
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

# Variable para mantener el valor por defecto de búsqueda
if "search_query_default" not in st.session_state:
    st.session_state["search_query_default"] = ""



# -------------------------------
# Barra lateral: Opciones de filtrado
# -------------------------------
st.sidebar.markdown("<h2 class='sidebar-header'>Filtros</h2>", unsafe_allow_html=True)

# Filtro por fuente (source)
fuentes = sorted(df_glosary["source"].dropna().astype(str).unique())
fuentes_seleccionadas = st.sidebar.multiselect("Filtrar por fuente(s):", options=fuentes)

if fuentes_seleccionadas:
    df_filtrado = df_glosary[df_glosary["source"].astype(str).isin(fuentes_seleccionadas)].copy()
else:
    df_filtrado = df_glosary.copy()

# Filtro por grupo (group)
grupos = sorted(df_filtrado["group"].dropna().astype(str).unique())
grupos_seleccionados = st.sidebar.multiselect("Filtrar por grupo(s):", options=grupos)

if grupos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["group"].astype(str).isin(grupos_seleccionados)].copy()


# -------------------------------
# Búsqueda avanzada (texto libre) con autocompletado
# -------------------------------
st.sidebar.markdown("### Búsqueda avanzada")
operador = st.sidebar.selectbox("Operador lógico:", options=["AND", "OR"], index=0)

# Campo de búsqueda en la barra lateral
search_query = st.sidebar.text_input("Ingrese término(s) de búsqueda:", value=st.session_state["search_query_default"], key="search_query")

umbral = st.sidebar.slider("🔍 Umbral de coincidencia (fuzz.partial_ratio)", min_value=0, max_value=100, value=100, step=1)


# Botón para guardar la búsqueda actual en el historial
if st.sidebar.button("Guardar búsqueda"):
    query = search_query.strip()
    if query and query not in st.session_state["search_history"]:
        st.session_state["search_history"].append(query)
        st.success("Búsqueda guardada en el historial.")

# Expander para mostrar el historial de búsquedas
with st.sidebar.expander("Historial de búsquedas"):
    if st.session_state["search_history"]:
        for i, hist in enumerate(st.session_state["search_history"]):
            if st.button(hist, key=f"history_{i}"):
                st.session_state["search_query_default"] = hist
                st.rerun()
    else:
        st.write("No hay búsquedas guardadas aún.")

def get_suggestions(query, df):
    suggestions = set()
    if query:
        for txt in df["text"].dropna():
            for word in str(txt).split():
                if word.lower().startswith(query.lower()):
                    suggestions.add(word)
    return sorted(list(suggestions))[:5]

sugerencias = get_suggestions(search_query, df_filtrado)
if sugerencias:
    st.markdown("**Sugerencias:**")
    for sug in sugerencias:
        if st.button(sug, key=f"sugg_{sug}"):
            st.session_state["search_query_default"] = sug
            st.rerun()

# Función para resaltar términos en el texto
def resaltar_texto(texto, terminos):
    for t in terminos:
        texto = texto.replace(t, f"<span style='background-color:yellow'>{t}</span>")
    return texto

# Función para evaluar cada fila usando fuzzy matching
def match_row(row, terminos, operador="AND", umbral=umbral):
    campos = [str(row[col]) for col in ["source", "text", "group", "code"] if col in row and pd.notnull(row[col])]
    combinado = " ".join(campos).lower()
    if operador == "AND":
        return all(fuzz.partial_ratio(t.lower(), combinado) >= umbral for t in terminos)
    else:
        return any(fuzz.partial_ratio(t.lower(), combinado) >= umbral for t in terminos)

# Separar términos de búsqueda (múltiples palabras)
terminos_busqueda = [t.strip() for t in search_query.split() if t.strip()]

# Aplicar filtro fuzzy si se ingresaron términos
if terminos_busqueda:
    df_filtered_fuzzy = df_filtrado[df_filtrado.apply(lambda row: match_row(row, terminos_busqueda, operador), axis=1)]
else:
    df_filtered_fuzzy = df_filtrado

st.subheader("Resultados de búsqueda")

# Mostrar resultados con términos resaltados y código en mayúsculas
if not fuentes_seleccionadas and not terminos_busqueda:
    st.info(
        "No se han seleccionado filtros. "
        "Por favor, elige una fuente en la barra lateral o ingresa un término de búsqueda. "
        "Fuentes disponibles: " + ", ".join(fuentes)
    )
    if st.checkbox("Mostrar tabla completa", key="full_table_none"):
        st.dataframe(df_glosary)
else:
    if not df_filtered_fuzzy.empty:
        for idx, row in df_filtered_fuzzy.iterrows():
            # Convertir la información del campo "code" a mayúsculas antes de resaltar
            code_resaltado = resaltar_texto(str(row['code']).upper(), terminos_busqueda)
            text_resaltado = resaltar_texto(str(row['text']), terminos_busqueda)
            group_resaltado = resaltar_texto(str(row['group']), terminos_busqueda)
            source_resaltado = resaltar_texto(str(row['source']), terminos_busqueda)
            link_html = ""
            if pd.notnull(row.get('Link')):
                link_html = " | <a href='" + str(row['Link']) + "' target='_blank'>Más información</a>"
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">{code_resaltado}</div>
                    <div class="card-text">{text_resaltado}</div>
                    <div class="card-footer">
                        <strong>grupo:</strong> {group_resaltado} | 
                        <strong>fuente:</strong> {source_resaltado} {link_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        if st.checkbox("Mostrar tabla completa", key="full_table_filtered"):
            st.dataframe(df_filtered_fuzzy)
    else:
        st.write("No se encontraron resultados. Intenta ajustar los filtros o el término de búsqueda.")
