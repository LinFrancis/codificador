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
    expected_columns = ["source", "text", "group", "code", "Link"]
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

st.info("✍️ Edita directamente la tabla, agrega nuevas entradas o elimina filas seleccionadas. Los cambios se guardan automáticamente.")

# =========================
# 📝 TABLA EDITABLE
# =========================
st.subheader("📋 Glosario editable")
edited_df = st.data_editor(
    df_glosary,
    use_container_width=True,
    num_rows="dynamic",
    key="editor_table"
)

if st.button("💾 Guardar cambios en la tabla"):
    try:
        save_data(edited_df)
        st.success("✅ Cambios guardados exitosamente en Google Sheets.")
    except Exception as e:
        st.error("❌ Error al guardar los cambios:")
        st.exception(e)

st.divider()

# =========================
# ➕ AGREGAR NUEVA ENTRADA
# =========================
st.subheader("➕ Agregar nueva entrada")
df_glosary = read_data()
existing_sources = sorted(df_glosary["source"].dropna().astype(str).unique())
existing_groups = sorted(df_glosary["group"].dropna().astype(str).unique())

with st.form("add_entry_form", clear_on_submit=True):
    use_custom_source = st.checkbox("✏️ Escribir nueva fuente")
    if use_custom_source or not existing_sources:
        new_source = st.text_input("Nueva fuente")
    else:
        new_source = st.selectbox("Fuente existente:", existing_sources, key="select_source")

    new_text = st.text_area("Texto")

    use_custom_group = st.checkbox("✏️ Escribir nuevo grupo")
    if use_custom_group or not existing_groups:
        new_group = st.text_input("Nuevo grupo")
    else:
        new_group = st.selectbox("Grupo existente:", existing_groups, key="select_group")

    new_code = st.text_input("Código")
    new_link = st.text_input("Link (opcional)")

    if st.form_submit_button("➕ Agregar entrada"):
        source_val = new_source.strip() if use_custom_source or not existing_sources else new_source
        group_val = new_group.strip() if use_custom_group or not existing_groups else new_group

        if not new_text.strip() or not source_val or not group_val:
            st.warning("⚠️ Los campos 'Texto', 'Fuente' y 'Grupo' son obligatorios.")
        else:
            new_row = {
                "source": source_val,
                "text": new_text.strip(),
                "group": group_val,
                "code": new_code.strip(),
                "Link": new_link.strip()
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
