import streamlit as st
import pandas as pd
import datetime
import csv
import os
from rapidfuzz import fuzz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ FIRST Streamlit command
st.set_page_config(
    page_title="Codificator 3001 - Dra. Javiera Saavedra Nazer",
    layout="wide",
    initial_sidebar_state="expanded")

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

st.subheader("📝 Editar glosario completo")

# Editable data table
edited_df = st.data_editor(
    df_glosary,
    use_container_width=True,
    num_rows="dynamic",  # Allows adding new rows
    key="editor_table"
)

# Confirm before overwrite
if st.checkbox("✅ Confirmo que deseo sobrescribir el contenido completo del glosario"):
    if st.button("💾 Guardar cambios en Google Sheets"):
        try:
            # Clear existing sheet
            sheet_by_name.clear()

            # Write updated DataFrame back to sheet
            sheet_by_name.append_row(edited_df.columns.tolist())  # Write headers
            sheet_by_name.append_rows(edited_df.values.tolist())  # Write all data

            st.success("✅ Cambios guardados exitosamente en Google Sheets.")
        except Exception as e:
            st.error("❌ Error al guardar los cambios:")
            st.exception(e)
else:
    st.info("Marca la casilla para confirmar que quieres sobrescribir el glosario antes de guardar.")


