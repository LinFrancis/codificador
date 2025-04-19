import streamlit as st
import pandas as pd
import datetime
import csv
import os
from rapidfuzz import fuzz  # Asegúrate de tener instalado rapidfuzz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

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

    # ✅ DEBUG: Print all accessible sheet titles
    try:
        sheet_titles = [s.title for s in client.openall()]
        st.success("✅ Sheets your app can access:")
        st.write(sheet_titles)
    except Exception as e:
        st.error("❌ Could not list spreadsheets:")
        st.exception(e)

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




st.set_page_config(
    page_title="Codificator 3001 - Dra. Javiera Saavedra Nazer",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Título y descripción (con contenedor de degradado)
st.markdown("""
<div class="title-container">
    <h1 class="title-text">Codificator 3001</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Bienvenida Dra. Javiera Saavedra Nazer**   
Soy el **Codificator 3001 🤖** y estoy a **su servicio**.

🔍 Utilice la **barra lateral** para filtrar las entradas por **fuente** y/o **grupo** mediante los menús desplegables.  
🧠 También puede usar el campo de **búsqueda avanzada** a continuación para ingresar uno o varios términos (use `"AND"` o `"OR"`) y encontrar rápidamente textos o títulos que los contengan.

📎 [**LinkedIn de la Dra. Javiera Saavedra Nazer**](https://www.linkedin.com/in/javiera-saavedra-nazer-md-faadv-582a7448/)
""")

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
def match_row(row, terminos, operador="AND", umbral=70):
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

st.subheader("Resultados de búsqueda del glosario")

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
