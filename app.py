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

# Configuración página
st.set_page_config(
    page_title="Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Dashboard Stock Operacional")

# Menú
menu = st.sidebar.radio("Selecciona vista:", [
    "Resumen General",
    "Producción Total Mensual",
    "Detalle por Trabajador",
    "Proyección de Meta"
])

# Subida de archivo
if menu == "Resumen General":
    uploaded_file = st.file_uploader("Sube el archivo Excel actualizado", type=["xlsx"])
    if uploaded_file:
        archivo = uploaded_file
        st.success("✅ Archivo cargado correctamente.")
    else:
        archivo = "excel/reporte.xlsx"
        st.info("ℹ️ Se usará el archivo por defecto.")
else:
    archivo = "excel/reporte.xlsx"

try:
    # Carga
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

    # Vista: Resumen General
    if menu == "Resumen General":
        total_stock = len(df)
        total_20 = len(df[df['TIPO_ERROR'] == 'Error 20'])
        total_28 = len(df[df['TIPO_ERROR'] == 'Error 28'])
        total_reg = len(df[df['ESTADO FINAL'] == 'REGULARIZADA'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TOTAL STOCK", formato_miles_punto(total_stock))
        col2.metric("Error 28", formato_miles_punto(total_28))
        col3.metric("Error 20", formato_miles_punto(total_20))
        col4.metric("Regularizadas", formato_miles_punto(total_reg))

        # Aquí puedes agregar el gráfico y tablas que ya tienes

    # Vista: Producción Total Mensual
    elif menu == "Producción Total Mensual":
        st.subheader("Producción Total Mensual")
        # Aquí agregas el bloque que tenías para esta vista

    # Vista: Detalle por Trabajador
    elif menu == "Detalle por Trabajador":
        st.subheader("Detalle por Trabajador")
        # Aquí agregas el bloque que tenías para esta vista

    # Vista: Proyección de Meta
    elif menu == "Proyección de Meta":
        st.title("📈 Proyección de Cumplimiento de Meta")

        responsables = ["Todo el equipo"] + sorted(df['Responsable'].dropna().unique())
        seleccionado = st.selectbox("Selecciona responsable", responsables)

        if seleccionado == "Todo el equipo":
            df_filtrado = df[(df['ESTADO FINAL'] == 'REGULARIZADA') & df['Fecha de cierre'].notna()].copy()
        else:
            df_filtrado = df[
                (df['Responsable'] == seleccionado) &
                (df['ESTADO FINAL'] == 'REGULARIZADA') &
                (df['Fecha de cierre'].notna())
            ].copy()

        hoy = pd.Timestamp.now().normalize()
        inicio_mes = hoy.replace(day=1)
        fin_mes = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])

        feriados = [
            pd.Timestamp("2025-06-21"),
            pd.Timestamp("2025-07-16"),
            pd.Timestamp("2025-09-18"),
            pd.Timestamp("2025-09-19"),
        ]

        calendario = pd.date_range(start=inicio_mes, end=fin_mes, freq='B')
        calendario = [d for d in calendario if d not in feriados]
        dias_habiles_hasta_hoy = len([d for d in calendario if d <= hoy])
        dias_habiles_restantes = len(calendario) - dias_habiles_hasta_hoy

        reg_actual = len(df_filtrado[(df_filtrado['Fecha de cierre'] >= inicio_mes) & (df_filtrado['Fecha de cierre'] <= hoy)])
        promedio_diario = reg_actual / dias_habiles_hasta_hoy if dias_habiles_hasta_hoy else 0
        proyeccion = reg_actual + promedio_diario * dias_habiles_restantes

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Avance actual (mes)", formato_miles_punto(reg_actual))
        col2.metric("Promedio diario (hábil)", f"{promedio_diario:.2f}")
        col3.metric("Proyección fin de mes", formato_miles_punto(int(proyeccion)))

        if seleccionado == "Todo el equipo":
            n = len(responsables) - 1
            meta_min, meta_med, meta_max = 350*n, 550*n, 850*n
        else:
            meta_min, meta_med, meta_max = 350, 550, 850

        col4.metric("Meta mínima", formato_miles_punto(meta_min))
        col5.metric("Meta máxima", formato_miles_punto(meta_max))

        if proyeccion >= meta_max:
            st.success("✅ Proyectas sobre la meta máxima.")
        elif proyeccion >= meta_min:
            st.success("👍 Cumplirías la meta mínima.")
        else:
            st.warning("⚠️ No alcanzarías la meta mínima.")

        dias = list(range(1, dias_habiles_hasta_hoy+1))
        acumulado = [promedio_diario*i for i in dias]
        df_chart = pd.DataFrame({"Día hábil": dias, "Acumulado": acumulado})

        base = alt.Chart(df_chart).mark_line(point=True).encode(
            x=alt.X('Día hábil:Q', title='Día hábil'),
            y=alt.Y('Acumulado:Q', title='Acumulado'),
            tooltip=[alt.Tooltip('Día hábil:Q', title='Día hábil'), alt.Tooltip('Acumulado:Q')]
        )

        hits = {"Meta mínima": meta_min, "Meta media": meta_med, "Meta máxima": meta_max}
        reglas = []
        for label, val in hits.items():
            reglas.append(
                alt.Chart(pd.DataFrame({'y': [val], 'label':[label]}))
                .mark_rule(color='green', strokeDash=[4,4])
                .encode(
                    y='y:Q',
                    tooltip=alt.Tooltip('label:N', title='Hito')
                )
            )

        chart = alt.layer(base, *reglas).properties(
            width=700, height=400,
            title="Avance acumulado con hitos referenciales"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
        st.caption("💡 Como dijo Peter Drucker: “Lo que no se mide, no se puede mejorar.”")

except Exception as e:
    st.error(f"❌ Error al procesar el archivo o generar el dashboard: {e}")
