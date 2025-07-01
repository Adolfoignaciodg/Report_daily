import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import altair as alt

# Paleta de colores
paleta_colores_anos = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948']

# Formato miles
def formato_miles_punto(x):
    try:
        if pd.isna(x):
            return "-"
        return f"{int(x):,}".replace(",", ".")
    except:
        return x

# Configuración
st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")
st.title("Dashboard Stock Operacional")

# Menú
menu = st.sidebar.radio("Selecciona vista:", [
    "Resumen General",
    "Producción Total Mensual",
    "Detalle por Trabajador",
    "Proyección de Meta"
])

# Archivo
if menu == "Resumen General":
    uploaded_file = st.file_uploader("Sube el archivo Excel actualizado", type=["xlsx"])
    if uploaded_file is not None:
        archivo = uploaded_file
        st.success("✅ Archivo cargado correctamente.")
    else:
        archivo = "excel/reporte.xlsx"
        st.info("ℹ️ Se usará el archivo por defecto.")
else:
    archivo = "excel/reporte.xlsx"

# Carga datos
try:
    df_20 = pd.read_excel(archivo, sheet_name="STOCK 20")
    df_20["TIPO_ERROR"] = "Error 20"

    df_28 = pd.read_excel(archivo, sheet_name="STOCK 28")
    df_28["TIPO_ERROR"] = "Error 28"

    df = pd.concat([df_20, df_28], ignore_index=True)
    df.columns = df.columns.str.strip()
    df.dropna(how='all', inplace=True)
    df = df[df['Responsable'].notna() & (df['Responsable'].str.strip() != '')]
    df['Responsable'] = df['Responsable'].astype(str).str.strip().str.lower().str.capitalize()
    df['ESTADO FINAL'] = df['ESTADO FINAL'].astype(str).str.strip().str.upper()
    df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
    df['Fecha de cierre'] = pd.to_datetime(df['Fecha de cierre'], dayfirst=True, errors='coerce')

    # Vistas
    if menu == "Resumen General":
        st.subheader("Resumen General")
        # Tu código aquí

    elif menu == "Producción Total Mensual":
        st.subheader("Producción Total Mensual")
        # Tu código aquí

    elif menu == "Detalle por Trabajador":
        st.subheader("Detalle por Trabajador")
        # Tu código aquí

    elif menu == "Proyección de Meta":
        st.subheader("Proyección de Meta")
        # Tu código aquí

except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
