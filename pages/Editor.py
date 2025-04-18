import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ CONFIGURACIÓN INICIAL
st.set_page_config(
    page_title="Codificator 3002 - Dra. Javiera Saavedra Nazer",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.logo("image/logo_codificator.png", size="large", link=None, icon_image="image/logo_codificator.png")


# ====================
# 🔐 PASSWORD PROTECTION with session + logout
# ====================
PASSWORD = "hellokitty"

# Initialize login state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Logout button
if st.session_state["authenticated"]:
    with st.sidebar:
        if st.button("🔓 Cerrar sesión"):
            st.session_state["authenticated"] = False
            st.rerun()

# Login screen
if not st.session_state["authenticated"]:
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("image/logo_codificator_4.png", width=200)
    with col2:
        st.markdown("""
        ### Estimada Dra. Javiera Saavedra Nazer""")  
        st.warning('El acceso a esta sección está restringido a personas autorizadas', icon="🔐")
        st.markdown("""
        Por favor, introduzca la contraseña correspondiente para continuar.  
        Si requiere asistencia, comuníquese con Su equipo de soporte.
        """)

        

        
        password = st.text_input("Contraseña:", type="password")
        if password == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        elif password:
            st.error("Contraseña incorrecta.")
            st.stop()
        else:
            st.stop()

    


# Layout in columns (image on left, welcome box on right)
col1, col2 = st.columns([1, 3])

with col1:
    st.image("image/logo_codificator_2.png", width=200)

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
        <h2>EDITOR DE BASE DE DATOS DE DIAGNÓSTICOS</h2>
        <p>✍️ Aquí puedes agregar nuevas entradas, editar contenido existente o eliminar filas seleccionadas.  
    Todos los cambios se guardan automáticamente en tiempo real.</p>
    """, unsafe_allow_html=True)





# ✅ CONEXIÓN A GOOGLE SHEET
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

SPREADSHEET_NAME = 'DIAGNOSIS_DATABASE'
SHEET_NAME = 'DIAGNOSIS'
sheet_by_name = connect_to_gsheet(SPREADSHEET_NAME, SHEET_NAME)

# ✅ FUNCIONES DE DATOS
def read_data():
    df = pd.DataFrame(sheet_by_name.get_all_records())
    df.reset_index(drop=True, inplace=True)
    df["row_id"] = df.index  # ✅ Add row_id for tracking edits
    return df

def save_data(df):
    expected_columns = ["source", "group", "code", "text"]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""
    df = df[expected_columns]  # Ensure column order
    sheet_by_name.clear()
    sheet_by_name.append_row(df.columns.tolist())
    sheet_by_name.append_rows(df.fillna("").values.tolist())

# ✅ CARGAR DATOS
df_glosary = read_data()


# === INICIALIZAR SESSION STATE ===
if "fuente_confirmada" not in st.session_state:
    st.session_state.fuente_confirmada = ""
if "grupo_confirmado" not in st.session_state:
    st.session_state.grupo_confirmado = ""

# === TABS ===
tabs = st.tabs(["➕ Agregar entrada", "📊 Ver/Editar", "🗑️ Eliminar"])

with tabs[0]:
    st.subheader("➕ Agregar nueva entrada")
    
    df_glosary = read_data()
    source_options =  ["Otro"] + sorted(df_glosary["source"].dropna().unique()) 
    group_options =  ["Otro"] + sorted(df_glosary["group"].dropna().unique())
    
    # === FORMULARIO DE FUENTE ===
    with st.form("form_fuente"):
        selected_source = st.selectbox("Selecciona fuente:", [""] + source_options)
        new_source = ""
        if selected_source == "Otro":
            new_source = st.text_input("Escribe nueva fuente:", key="new_source")
        submitted_fuente = st.form_submit_button("Confirmar fuente")
        if submitted_fuente:
            if (selected_source == "Otro" and not new_source.strip()) or selected_source == "":
                st.warning("⚠️ Debes ingresar o seleccionar una fuente.")
            else:
                st.session_state.fuente_confirmada = new_source.strip() if selected_source == "Otro" else selected_source.strip()
                st.success(f"Fuente confirmada: {st.session_state.fuente_confirmada}")
    
    # === FORMULARIO DE GRUPO ===
    with st.form("form_grupo"):
        selected_group = st.selectbox("Selecciona grupo:", [""] + group_options)
        new_group = ""
        if selected_group == "Otro":
            new_group = st.text_input("Escribe nuevo grupo:", key="new_group")
        submitted_grupo = st.form_submit_button("Confirmar grupo")
        if submitted_grupo:
            if (selected_group == "Otro" and not new_group.strip()) or selected_group == "":
                st.warning("⚠️ Debes ingresar o seleccionar un grupo.")
            else:
                st.session_state.grupo_confirmado = new_group.strip() if selected_group == "Otro" else selected_group.strip()
                st.success(f"Grupo confirmado: {st.session_state.grupo_confirmado}")
    
    # === FORMULARIO FINAL ===
    with st.form("form_final_entry", clear_on_submit=True):
        new_code = st.text_input("Código")
        new_text = st.text_area("Texto")
    
        if st.form_submit_button("Agregar entrada"):
            final_source = st.session_state.get("fuente_confirmada", "")
            final_group = st.session_state.get("grupo_confirmado", "")
    
            if not new_text.strip() or not final_source or not final_group:
                st.warning("⚠️ Los campos 'Texto', 'Fuente' y 'Grupo' son obligatorios.")
            else:
                new_row = {
                    "source": final_source,
                    "group": final_group,
                    "code": new_code.strip(),
                    "text": new_text.strip()
                }
                try:
                    current_df = read_data()
                    updated_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(updated_df)
                    st.success("✅ Nueva entrada agregada correctamente.")
                    st.info(f"""
    **Fuente:** {new_row['source']}
    
    **Grupo:** {new_row['group']}
    
    **Código:** {new_row['code']}
    
    **Texto:** {new_row['text']}
    """)
                except Exception as e:
                    st.error("❌ Error al agregar la entrada:")
                    st.exception(e)
    
        if st.form_submit_button("🧹 Limpiar formulario"):
            st.session_state.fuente_confirmada = ""
            st.session_state.grupo_confirmado = ""
            st.rerun()

# st.divider()


with tabs[1]:
    st.subheader("📊 Ver, editar y eliminar entradas")

    df_glosary = read_data()

    # Filters
    source_filter = st.selectbox("Filtrar por fuente:", ["Todas"] + sorted(df_glosary['source'].dropna().unique()))
    group_filter = st.selectbox("Filtrar por grupo:", ["Todas"] + sorted(df_glosary['group'].dropna().unique()))

    filtered_df = df_glosary.copy()
    if source_filter != "Todas":
        filtered_df = filtered_df[filtered_df["source"] == source_filter]
    if group_filter != "Todas":
        filtered_df = filtered_df[filtered_df["group"] == group_filter]

    # 👉 Show editable table
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_glosary"
    )

    st.warning("ℹ️ Haz clic dos veces para que los cambios se guarden correctamente.")

    # 👉 Save button
    if st.button("💾 Guardar cambios"):
        try:
            full_df = read_data()
            for _, row in edited_df.iterrows():
                idx = int(row["row_id"])
                full_df.loc[idx, ["source", "group", "code", "text"]] = row[["source", "group", "code", "text"]]
            save_data(full_df)
            st.success("✅ Cambios guardados correctamente en Google Sheets.")
            st.rerun()
        except Exception as e:
            st.error("❌ Error al guardar los cambios:")
            st.exception(e)


    
def safe_format_row(i):
    match = df_glosary[df_glosary["row_id"] == i]
    if not match.empty:
        code = str(match.iloc[0]["code"])
        text = str(match.iloc[0]["text"])  # 🔐 fuerza texto seguro
        return f"{i}: {code} | {text[:40]}..."
    else:
        return f"{i}: (entrada no encontrada)"

with tabs[2]:
    st.markdown("### 🗑️ Seleccionar filas para eliminar")

    df_glosary = read_data()
    row_ids = df_glosary["row_id"]

    selected_rows = st.multiselect(
        "Selecciona las filas a eliminar:",
        row_ids,
        format_func=safe_format_row,
        key="delete_multiselect"
    )

    if selected_rows:
        col1, col2 = st.columns([1, 3])
        with col1:
            confirm = st.checkbox("⚠️ Confirmar eliminación")
        with col2:
            if confirm and st.button("🗑️ Eliminar seleccionadas"):
                try:
                    deleted_refs = []
                    for i in selected_rows:
                        match = df_glosary[df_glosary["row_id"] == i]
                        if not match.empty:
                            deleted_refs.append(f"{i}: {match.iloc[0]['code']} | {match.iloc[0]['text'][:40]}...")

                    updated_df = df_glosary[~df_glosary["row_id"].isin(selected_rows)]
                    save_data(updated_df)

                    st.success("✅ {} fila(s) eliminadas correctamente:\n{}".format(
                        len(deleted_refs), "\n".join(deleted_refs)
                    ))
                    st.rerun()

                except Exception as e:
                    st.error("❌ Error al eliminar filas:")
                    st.exception(e)
    else:
        st.write("No se han seleccionado filas para eliminar.")
