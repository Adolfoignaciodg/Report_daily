import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import altair as alt

# Paleta de colores uniforme y agradable para ambos gráficos
paleta_colores_anos = ["#4E79a7", "#F28E2B", "#59A14F", '#76B7B2', '#59A14F', '#EDC948']

def formato_miles_punto(x):
    try:
        if pd.isna(x):
            return "-"
        return f"{int(x):,}".replace(",", ".")
    except:
        return x

def cargar_y_limpiar_datos(archivo):
    df_20 = pd.read_excel(archivo, sheet_name="STOCK 20")
    df_20["TIPO_ERROR"] = "Error 20"

    df_28 = pd.read_excel(archivo, sheet_name="STOCK 28")
    df_28["TIPO_ERROR"] = "Error 28"

    df = pd.concat([df_20, df_28], ignore_index=True)
    df.columns = df.columns.str.strip()

    filas_antes = len(df)
    df.dropna(how='all', inplace=True)
    filas_despues = len(df)
    filas_eliminadas = filas_antes - filas_despues

    df = df[df['Responsable'].notna() & (df['Responsable'].str.strip() != '')]
    df['Responsable'] = df['Responsable'].astype(str).str.strip().str.lower().str.capitalize()
    df['ESTADO FINAL'] = df['ESTADO FINAL'].astype(str).str.strip().str.upper()
    df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
    df['Fecha de cierre'] = pd.to_datetime(df['Fecha de cierre'], dayfirst=True, errors='coerce')

    return df, filas_eliminadas

def mostrar_metricas(totales_dict):
    cols = st.columns(len(totales_dict))
    for col, (label, valor) in zip(cols, totales_dict.items()):
        col.metric(label, formato_miles_punto(valor))


#--- Mostrar tabla resumen de regularizadas por mes y año ---


def mostrar_tabla_resumen(resumen_mensual, meses_orden):
    tabla_resumen = resumen_mensual.pivot_table(index='Mes_nombre', columns='Año', values='Cantidad', fill_value=0)
    tabla_resumen = tabla_resumen.reindex(meses_orden)
    tabla_resumen_formateada = tabla_resumen.applymap(formato_miles_punto)
    st.subheader("Tabla de Regularizadas por Mes y Año")
    st.dataframe(tabla_resumen_formateada, use_container_width=True)




# --- Grafico de barras Agrupadas mes a mes por año ---


def grafico_regularizadas_mes_ano(df_reg_historico, titulo):
    años = sorted(df_reg_historico['Año'].unique())
    todos_los_meses = pd.DataFrame([(a, m) for a in años for m in range(1, 13)], columns=['Año', 'Mes'])

    resumen_mensual = df_reg_historico.groupby(['Año', 'Mes']).size().reset_index(name='Cantidad')
    resumen_mensual = pd.merge(todos_los_meses, resumen_mensual, on=['Año', 'Mes'], how='left').fillna(0)
    resumen_mensual['Cantidad'] = resumen_mensual['Cantidad'].astype(int)
    resumen_mensual['Mes_nombre'] = resumen_mensual['Mes'].apply(lambda x: calendar.month_name[x])
    
    meses_orden = list(calendar.month_name)[1:]  # Enero a Diciembre

    # 🔸 Calcular máximo + margen
    max_valor = resumen_mensual['Cantidad'].max()
    margen = int(max_valor * 0.10)

    color_scale = alt.Scale(
        domain=años,
        range=paleta_colores_anos
    )

    barras = alt.Chart(resumen_mensual).mark_bar().encode(
        x=alt.X('Mes_nombre:N', sort=meses_orden, title='Mes'),
        y=alt.Y('Cantidad:Q',
                title='Cantidad de Regularizadas',
                axis=alt.Axis(grid=True),
                scale=alt.Scale(domain=[0, max_valor + margen])),  # 👈 se ajusta el eje Y
        color=alt.Color('Año:N', scale=color_scale, legend=alt.Legend(title="Año")),
        xOffset='Año:N',
        tooltip=[
            alt.Tooltip('Mes_nombre:N', title='Mes'),
            alt.Tooltip('Año:N', title='Año'),
            alt.Tooltip('Cantidad:Q', title='Cantidad')
        ]
    )
    resumen_mensual['Cantidad_fmt'] = resumen_mensual['Cantidad'].apply(lambda x: f"{x:,}".replace(",", "."))
    etiquetas = alt.Chart(resumen_mensual).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=12,
        color='Black'
    ).encode(
        x=alt.X('Mes_nombre:N', sort=meses_orden),
        y=alt.Y('Cantidad:Q'),
        xOffset='Año:N',
        detail='Año:N',
        text=alt.Text('Cantidad_fmt:N'),
    )

    chart = (barras + etiquetas).properties(width=750, height=420, title=titulo).interactive()
    st.altair_chart(chart, use_container_width=True)

    return resumen_mensual, meses_orden



# Configuración de la página

st.set_page_config(
    page_title="Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Dashboard Stock Operacional")

# --- Selección de vista antes de cargar archivo ---
menu = st.sidebar.radio("Selecciona vista:", ["Resumen General", "Resumen Producción Total Mensual", "Detalle por Trabajador", "proyección de meta"])

# --- Subida de archivo solo si está en "Resumen General" ---
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

try:
    df, filas_eliminadas = cargar_y_limpiar_datos(archivo)

    if filas_eliminadas > 0:
        st.info(f"ℹ️ Se eliminaron {filas_eliminadas} filas completamente vacías del archivo.")

   
   
    # --------------------- VISTAS ---------------------
  
  
   #--- RESUMEN GENERAL ---
   
    if menu == "Resumen General":


        total_stock = len(df)
        total_20 = len(df[df['TIPO_ERROR'] == 'Error 20'])
        total_28 = len(df[df['TIPO_ERROR'] == 'Error 28'])
        total_reg = len(df[df['ESTADO FINAL'] == 'REGULARIZADA'])

        mostrar_metricas({
            "TOTAL STOCK": total_stock,
            "Error 28": total_28,
            "Error 20": total_20,
            "Regularizadas": total_reg
        })


        #---DESGLOSE DE REGULARIZACIONES POR PROGRAMA CON PORCENTAJE---

        df_reg = df[df['ESTADO FINAL'] == 'REGULARIZADA']
        programas = ['Tradicional', 'Reactiva', 'Chile Apoya', 'COVID']
        conteo_programas = {p: len(df_reg[df_reg['PROGRAMA'].str.strip().str.upper() == p.upper()]) for p in programas}
        total_prog = sum(conteo_programas.values())
        desglose_programas = []
        for p in programas:
            cant = conteo_programas[p]
            porc = (cant / total_prog * 100) if total_prog > 0 else 0
            desglose_programas.append(f"**{p}:** {formato_miles_punto(cant)} ({porc:.1f}%)")
        st.markdown(" - ".join(desglose_programas))

            #---RESUMEN DE OPERACIONES TOTALES ASIGNADAS---

        st.markdown("---")
        st.subheader("Asignaciones Totales por Colaborador y Tipo de Error")

        df_resumen = df[df['TIPO_ERROR'].notna() & (df['TIPO_ERROR'].str.strip() != '')]
        resumen = df_resumen.groupby(["Responsable", "TIPO_ERROR"]).size().unstack(fill_value=0)
        resumen["TOTAL"] = resumen.sum(axis=1)
        resumen = resumen.sort_values("TOTAL", ascending=False)
        resumen_display = resumen.applymap(formato_miles_punto)
        st.dataframe(resumen_display, use_container_width=True)

        # --- GRAFICO DE BARRAS AGRUPADAS: POR MES Y AÑO ---
# 👇 Espacio visual antes del gráfico
        st.markdown("<br>", unsafe_allow_html=True)   # 1 salto
        st.markdown("<br><br>", unsafe_allow_html=True)  # 2 saltos
        df_reg_historico = df_reg.copy()
        df_reg_historico = df_reg_historico[df_reg_historico['Fecha de cierre'].notna()]
        df_reg_historico['Año'] = df_reg_historico['Fecha de cierre'].dt.year
        df_reg_historico['Mes'] = df_reg_historico['Fecha de cierre'].dt.month

        resumen_mensual, meses_orden = grafico_regularizadas_mes_ano(df_reg_historico, "Regularizaciones por Mes y Año (Barras Agrupadas)")
        mostrar_tabla_resumen(resumen_mensual, meses_orden) 
        
 


#--- DETALLE PRODUCCIÓN TOTAL MENSUAL --- 

    elif menu == "Resumen Producción Total Mensual":
        st.subheader("Resumen Producción Total Mensual")

        df_reg = df[df['ESTADO FINAL'] == 'REGULARIZADA'].copy()
        df_reg = df_reg[df_reg['Fecha de cierre'].notna()]

        hoy = datetime.now()
        años_disponibles = sorted(df_reg['Fecha de cierre'].dt.year.dropna().unique())
        año_default = hoy.year if hoy.year in años_disponibles else años_disponibles[-1]
        año = st.selectbox("Selecciona Año", años_disponibles, index=años_disponibles.index(año_default))

        meses_disponibles = sorted(df_reg[df_reg['Fecha de cierre'].dt.year == año]['Fecha de cierre'].dt.month.unique())
        mes_default = hoy.month if hoy.month in meses_disponibles else meses_disponibles[-1]
        mes = st.selectbox("Selecciona Mes", meses_disponibles, index=meses_disponibles.index(mes_default), format_func=lambda x: calendar.month_name[x])

        actual = df_reg[(df_reg['Fecha de cierre'].dt.month == mes) & (df_reg['Fecha de cierre'].dt.year == año)]

        total_20 = len(actual[actual['TIPO_ERROR'] == 'Error 20'])
        total_28 = len(actual[actual['TIPO_ERROR'] == 'Error 28'])
        total = len(actual)

        col1, col2, col3 = st.columns(3)
        col1.metric(f"Error 28 ({calendar.month_name[mes]} {año})", formato_miles_punto(total_28))
        col2.metric(f"Error 20 ({calendar.month_name[mes]} {año})", formato_miles_punto(total_20))
        col3.metric("Total del Mes", formato_miles_punto(total))

        st.caption("Solo se consideran operaciones REGULARIZADAS con Fecha de cierre")

        if not actual.empty:
            conteo = actual.groupby([actual['Fecha de cierre'].dt.strftime("%d-%m-%Y"), 'TIPO_ERROR']).size().unstack(fill_value=0)
            conteo.index = pd.to_datetime(conteo.index, format="%d-%m-%Y")
            conteo = conteo.sort_index()
            conteo.index = conteo.index.strftime("%d-%m-%Y")
            conteo['TOTAL DIARIO'] = conteo.sum(axis=1)

            st.markdown(f"#### Detalle de Producción: {calendar.month_name[mes]} {año}")
            st.dataframe(conteo, use_container_width=True)
        else:
            st.info("No hay operaciones REGULARIZADAS este mes.")


#--- DETALLE POR TRABAJADOR ---

    elif menu == "Detalle por Trabajador":
        responsables = sorted(df['Responsable'].dropna().unique())
        seleccionado = st.selectbox("Selecciona un responsable", responsables)

        df_resp = df[df['Responsable'] == seleccionado]
        hoy = pd.Timestamp.now()
        hace_un_mes = hoy - pd.DateOffset(months=1)

        fechas_validas = df_resp[(df_resp['ESTADO FINAL'] == 'REGULARIZADA') & (df_resp['Fecha de cierre'].notna())]['Fecha de cierre']
        año_default = fechas_validas.max().year if not fechas_validas.empty else hoy.year
        mes_default = fechas_validas.max().month if not fechas_validas.empty else hoy.month

        años_disponibles = sorted(df['FECHA'].dt.year.dropna().unique())
        año_index = años_disponibles.index(año_default) if año_default in años_disponibles else 0
        año = st.selectbox("Año", años_disponibles, index=año_index)

        meses_disponibles = sorted(df['FECHA'][df['FECHA'].dt.year == año].dt.month.unique())
        mes_index = meses_disponibles.index(mes_default) if mes_default in meses_disponibles else 0
        mes = st.selectbox("Mes", options=meses_disponibles, index=mes_index, format_func=lambda x: calendar.month_name[x])

        df_mes = df_resp[
            (df_resp['Fecha de cierre'].dt.year == año) &
            (df_resp['Fecha de cierre'].dt.month == mes) &
            (df_resp['ESTADO FINAL'] == 'REGULARIZADA')
        ]
        total_reg = len(df_mes)

        en_revision = df_resp[df_resp['ESTADO FINAL'] == 'EN REVISIÓN']
        pendiente = df_resp[df_resp['ESTADO FINAL'] == 'PENDIENTE']
        total_rev = len(en_revision)
        total_pen = len(pendiente)

        atrasadas = df_resp[
            (df_resp['ESTADO FINAL'].isin(['EN REVISIÓN', 'PENDIENTE'])) &
            (df_resp['FECHA'] < hace_un_mes)
        ]
        total_atrasadas = len(atrasadas)

        otros_estados = [
            "PENDIENTE BANCO", "CONSULTA BANCO", "OP EQUIPO COBRO",
            "CADUCADA", "RECHAZO FORMAL", "NO APLICA", "REVERSADA"
        ]
        otros = df_resp[df_resp['ESTADO FINAL'].isin(otros_estados)]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("REGULARIZADAS", formato_miles_punto(total_reg))
        col2.metric("EN REVISIÓN", formato_miles_punto(total_rev))
        col3.metric("PENDIENTE", formato_miles_punto(total_pen))
        col4.metric("OTROS ESTADOS", formato_miles_punto(len(otros)))
        col5.metric("ATRASADAS", formato_miles_punto(total_atrasadas))

        st.markdown(f"### Detalle REGULARIZADAS en {calendar.month_name[mes]} {año}")
        if not df_mes.empty:
            resumen_dia = df_mes.groupby(df_mes['Fecha de cierre'].dt.day).size().reset_index(name='Cantidad')
            resumen_dia.columns = ['Día', 'Cantidad']
            st.dataframe(resumen_dia.set_index('Día'), use_container_width=True)
            st.success(f"Total regularizadas: {formato_miles_punto(total_reg)}")
        else:
            st.info("No hay regularizadas este mes.")

        st.markdown("### Resumen mensual de regularizadas")

        df_reg_historico = df_resp[
            (df_resp['ESTADO FINAL'] == 'REGULARIZADA') &
            (df_resp['Fecha de cierre'].notna())
        ].copy()
        df_reg_historico['Año'] = df_reg_historico['Fecha de cierre'].dt.year
        df_reg_historico['Mes'] = df_reg_historico['Fecha de cierre'].dt.month

        resumen_mensual, meses_orden = grafico_regularizadas_mes_ano(df_reg_historico, f"Regularizadas mes a mes por año - {seleccionado}")

        st.markdown("### Detalle mensual de operaciones ATRASADAS (todo histórico)")
        if not atrasadas.empty:
            atrasadas_detalle = atrasadas.copy()
            atrasadas_detalle['Año'] = atrasadas_detalle['FECHA'].dt.year
            atrasadas_detalle['Mes'] = atrasadas_detalle['FECHA'].dt.month.apply(lambda x: calendar.month_name[x])
            resumen_atrasadas = atrasadas_detalle.groupby(['Año', 'Mes']).size().reset_index(name='Cantidad')
            st.dataframe(resumen_atrasadas, use_container_width=True)
        else:
            st.info("No hay operaciones atrasadas para este responsable.")

        st.markdown("### Detalle mensual de OTROS ESTADOS (todo histórico)")
        if not otros.empty:
            otros_detalle = otros.copy()
            otros_detalle['Año'] = otros_detalle['FECHA'].dt.year
            otros_detalle['Mes'] = otros_detalle['FECHA'].dt.month.apply(lambda x: calendar.month_name[x])
            resumen_otros = otros_detalle.groupby(['Año', 'Mes', 'ESTADO FINAL']).size().reset_index(name='Cantidad')
            st.dataframe(resumen_otros, use_container_width=True)
        else:
            st.info("No hay operaciones en otros estados para este responsable.")


    #--- PROYECCIÓN DE META ---


    elif menu == "proyección de meta":
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
        calendario = [d for d in calendario if d not in feriados and d <= hoy]

        df_filtrado['Fecha'] = pd.to_datetime(df_filtrado['Fecha de cierre']).dt.normalize()

        df_mes = df_filtrado[(df_filtrado['Fecha'] >= inicio_mes) & (df_filtrado['Fecha'] <= hoy)]
        dias_operativos = len(calendario)

        # Operaciones realizadas por día
        ops_por_dia = df_mes.groupby('Fecha').size()
        ops_por_dia = ops_por_dia.reindex(calendario, fill_value=0)

        ops_cum = ops_por_dia.cumsum()

        # Meta mensual (ajustar según necesidad)
        meta_mensual = 210
        st.write(f"Meta mensual: {meta_mensual}")

        st.line_chart(ops_cum)

        ultimo_dia = calendario[-1] if calendario else hoy
        proyeccion = (ops_cum.iloc[-1] / len(calendario)) * len(pd.date_range(inicio_mes, fin_mes, freq='B'))
        st.write(f"Proyección para fin de mes: {int(proyeccion)}")

except Exception as e:
    st.error(f"❌ Error al procesar el archivo o generar el dashboard: {e}")

