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

# =========================
# ➕ AGREGAR NUEVA ENTRADA
# =========================
st.subheader("➕ Agregar nueva entrada")

with st.form("add_simple_entry_form", clear_on_submit=True):
    new_source = st.text_input("Fuente")
    new_group = st.text_input("Grupo")
    new_code = st.text_input("Código")
    new_text = st.text_area("Texto")

    if st.form_submit_button("Agregar entrada"):
        if not new_text.strip() or not new_source.strip() or not new_group.strip():
            st.warning("⚠️ Los campos 'Texto', 'Fuente' y 'Grupo' son obligatorios.")
        else:
            new_row = {
                "source": new_source.strip(),
                "group": new_group.strip(),
                "code": new_code.strip(),
                "text": new_text.strip()
            }
            try:
                current_df = read_data()
                updated_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(updated_df)
                st.success("✅ Nueva entrada agregada correctamente.")
            except Exception as e:
                st.error("❌ Error al agregar la entrada:")
                st.exception(e)

st.divider()

# =========================
# 🗑️ ELIMINAR ENTRADAS
# =========================
st.subheader("🗑️ Eliminar entradas")
df_glosary = read_data()
df_glosary["_index"] = df_glosary.index
selected_rows = st.multiselect(
    "Selecciona las filas a eliminar:",
    df_glosary["_index"],
    format_func=lambda i: f"{i}: {df_glosary.loc[i, 'text'][:30]}..."
)

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
