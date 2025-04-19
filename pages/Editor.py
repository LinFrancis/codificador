import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ CONFIGURACIÓN INICIAL
st.set_page_config(
    page_title="Codificator 3001 - Dra. Javiera Saavedra Nazer",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    return pd.DataFrame(sheet_by_name.get_all_records())

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
st.title("Codificator 3001")
df_glosary = read_data()

st.info("✍️ Agrega nuevas entradas o elimina filas seleccionadas. Los cambios se guardan automáticamente.")

# === INICIALIZAR SESSION STATE ===
if "fuente_confirmada" not in st.session_state:
    st.session_state.fuente_confirmada = ""
if "grupo_confirmado" not in st.session_state:
    st.session_state.grupo_confirmado = ""

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
        st.experimental_rerun()

st.divider()


# =========================
# 📊 VISUALIZAR Y ELIMINAR BASE DE DATOS
# =========================
st.subheader("📊 Ver y eliminar entradas del glosario")
df_glosary = read_data()
df_glosary["_index"] = df_glosary.index

with st.expander("Mostrar tabla completa y seleccionar filas a eliminar"):
    selected_rows = st.multiselect(
        "Selecciona las filas a eliminar:",
        df_glosary["_index"],
        format_func=lambda i: f"{i}: {df_glosary.loc[i, 'text'][:30]}..."
    )
    st.dataframe(df_glosary.drop(columns=["_index"]), use_container_width=True)

    if selected_rows:
        col1, col2 = st.columns([1, 3])
        with col1:
            confirm = st.checkbox("⚠️ Confirmar eliminación")
        with col2:
            if confirm and st.button("🗑️ Eliminar seleccionadas"):
                try:
                    updated_df = df_glosary.drop(index=selected_rows).reset_index(drop=True)
                    save_data(updated_df)
                    st.success(f"✅ {len(selected_rows)} fila(s) eliminadas correctamente.")
                except Exception as e:
                    st.error("❌ Error al eliminar filas:")
                    st.exception(e)
    else:
        st.write("No se han seleccionado filas para eliminar.")


