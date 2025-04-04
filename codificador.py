import streamlit as st
import pandas as pd
import datetime
import csv
import os
from rapidfuzz import fuzz  # Asegúrate de tener instalado rapidfuzz

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
Bienvenida Dra. Javiera Saavedra Nazer. Soy el codificator 3001 y estoy a tu servicio.
 
Utiliza la barra lateral para filtrar las entradas por **fuente** y/o **grupo** mediante el menú desplegable y utiliza el campo de búsqueda avanzado a continuación para ingresar uno o varios términos (usa "AND" u "OR") y encontrar rápidamente textos o títulos que contengan esos términos.

**[LinkedIn de la Dra. Javiera Saavedra Nazer](https://www.linkedin.com/in/javiera-saavedra-nazer-md-faadv-582a7448/)**
""")

# Inicializar el historial de búsqueda en la sesión
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []

# Variable para mantener el valor por defecto de búsqueda
if "search_query_default" not in st.session_state:
    st.session_state["search_query_default"] = ""

# Cargar datos del glosario
@st.cache_data
def load_glosary():
    file_path_glosary = "DIAGNOSIS TEXT_full.xlsx"  # Asegúrate que el nombre y la ruta sean exactos
    if not os.path.exists(file_path_glosary):
        st.error(f"El archivo '{file_path_glosary}' no se encontró. Asegúrate de que esté subido en el repositorio.")
        st.stop()
    return pd.read_excel(file_path_glosary)

df_glosary = load_glosary()

# -------------------------------
# Barra lateral: Opciones de filtrado
# -------------------------------
st.sidebar.markdown("<h2 class='sidebar-header'>Filtros</h2>", unsafe_allow_html=True)
fuentes = sorted(df_glosary["source"].dropna().astype(str).unique())
fuente_seleccionada = st.sidebar.selectbox("Filtrar por fuente:", options=["None"] + fuentes)

# Filtrar según fuente
if fuente_seleccionada != "None":
    df_filtrado = df_glosary[df_glosary["source"].astype(str) == fuente_seleccionada].copy()
else:
    df_filtrado = df_glosary.copy()

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
if fuente_seleccionada == "None" and not terminos_busqueda:
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
