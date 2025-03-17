import streamlit as st
import pandas as pd
import datetime
import csv
import os

st.set_page_config(
    page_title="Codificador - Dra. Javiersa Saavedra Nazer",
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

# Título y descripción (ahora dentro de un contenedor con degradado).
st.markdown("""
<div class="title-container">
    <h1 class="title-text">Codificador - Dra. Javiersa Saavedra Nazer</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Bienvenido al Codificador - Dra. Javiersa Saavedra Nazer –  
Utiliza la barra lateral para filtrar las entradas por **fuente** mediante el menú desplegable y el menú de búsqueda a continuación para encontrar rápidamente textos o títulos específicos.

**[LinkedIn de la Dra. Javiersa Saavedra Nazer](https://www.linkedin.com/in/javiera-saavedra-nazer-md-faadv-582a7448/)**
""")

# Cargar datos del glosario comprobando si el archivo existe.
@st.cache_data
def load_glosary():
    file_path_glosary = "DIAGNOSIS text_fulll.xlsx"  # Actualiza el nombre del archivo si es necesario
    if not os.path.exists(file_path_glosary):
        st.error(f"El archivo '{file_path_glosary}' no se encontró. Asegúrate de que esté subido en el repositorio.")
        return pd.DataFrame()  # Retorna un DataFrame vacío para evitar errores posteriores.
    return pd.read_excel(file_path_glosary)

df_glosary = load_glosary()

# -------------------------------
# Barra lateral: Opciones de filtrado
# -------------------------------
st.sidebar.markdown("<h2 class='sidebar-header'>Filtros</h2>", unsafe_allow_html=True)

# Convertir la columna "source" a string para evitar errores
fuentes = sorted(df_glosary["source"].dropna().astype(str).unique())
fuente_seleccionada = st.sidebar.selectbox("Filtrar por fuente:", options=["None"] + fuentes)

# -------------------------------
# Página principal: Búsqueda y resultados
# -------------------------------
# Determinar categorías disponibles según el filtro de fuente
if fuente_seleccionada != "None":
    df_fuente_filtrado = df_glosary[df_glosary["source"].astype(str) == fuente_seleccionada]
else:
    df_fuente_filtrado = df_glosary

# Convertir los códigos a string para evitar problemas de orden
categorias = sorted(df_fuente_filtrado["code"].dropna().astype(str).unique())
palabra_clave = st.selectbox("Buscar:", options=["None"] + categorias)

# Filtrar el DataFrame
df_filtrado = df_glosary.copy()
if fuente_seleccionada != "None":
    df_filtrado = df_filtrado[df_filtrado["source"].astype(str) == fuente_seleccionada]
if palabra_clave != "None":
    df_filtrado = df_filtrado[
        df_filtrado["source"].astype(str).str.contains(palabra_clave, case=False, na=False) |
        df_filtrado["text"].astype(str).str.contains(palabra_clave, case=False, na=False) |
        df_filtrado["group"].astype(str).str.contains(palabra_clave, case=False, na=False) |
        df_filtrado["code"].astype(str).str.contains(palabra_clave, case=False, na=False)
    ]

st.subheader("Resultados de búsqueda del glosario")

# Mostrar resultados
if fuente_seleccionada == "None" and palabra_clave == "None":
    st.info(
        "No se han seleccionado filtros. "
        "Por favor, elige una fuente en la barra lateral para ver los resultados filtrados. "
        "Fuentes disponibles: " + ", ".join(fuentes)
    )
    if st.checkbox("Mostrar tabla completa", key="full_table_none"):
        st.dataframe(df_glosary)
else:
    if not df_filtrado.empty:
        for idx, row in df_filtrado.iterrows():
            link_html = ""
            if pd.notnull(row.get('Link')):
                link_html = " | <a href='" + str(row['Link']) + "' target='_blank'>Más información</a>"
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">{row['code']}</div>
                    <div class="card-text">{row['text']}</div>
                    <div class="card-footer">
                        <strong>grupo:</strong> {row['group']} | 
                        <strong>fuente:</strong> {row['source']} {link_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        if st.checkbox("Mostrar tabla completa", key="full_table_filtered"):
            st.dataframe(df_filtrado)
    else:
        st.write("No se encontraron resultados. Intenta ajustar los filtros o las palabras clave de búsqueda.")
