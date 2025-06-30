# --- Otras condiciones anteriores ---

elif menu == "Detalle por Trabajador":
    # ... código original que ya tienes para detalle por trabajador ...

elif menu == "proyección de meta":
    st.title("📈 Proyección de Cumplimiento de Meta")
    
    # Filtro: Seleccionar responsable o todo el equipo
    responsables = ["Todo el equipo"] + sorted(df['Responsable'].dropna().unique())
    seleccionado = st.selectbox("Selecciona responsable", responsables)
    
    # Filtra según responsable y solo regularizadas con fecha de cierre válida
    if seleccionado == "Todo el equipo":
        df_filtrado = df[(df['ESTADO FINAL'] == 'REGULARIZADA') & df['Fecha de cierre'].notna()].copy()
    else:
        df_filtrado = df[
            (df['Responsable'] == seleccionado) &
            (df['ESTADO FINAL'] == 'REGULARIZADA') &
            (df['Fecha de cierre'].notna())
        ].copy()

    # Fechas clave
    hoy = pd.Timestamp.now().normalize()
    inicio_mes = hoy.replace(day=1)
    fin_mes = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])
    
    # Lista de feriados (puedes mejorar cargando un archivo o API)
    feriados = [
        pd.Timestamp("2025-06-21"),  # Pueblos originarios
        pd.Timestamp("2025-07-16"),  # Virgen del Carmen
        pd.Timestamp("2025-09-18"),  # Fiestas Patrias
        pd.Timestamp("2025-09-19"),
        # Agrega más...
    ]

    # Generar rango de días hábiles en el mes (lunes a viernes, sin feriados)
    calendario = pd.date_range(start=inicio_mes, end=fin_mes, freq='B')
    calendario = [d for d in calendario if d not in feriados]

    dias_habiles_totales = len(calendario)
    dias_habiles_hasta_hoy = len([d for d in calendario if d <= hoy])
    dias_habiles_restantes = dias_habiles_totales - dias_habiles_hasta_hoy

    # Avance actual: cantidad de regularizadas entre inicio mes y hoy
    reg_actual = len(df_filtrado[
        (df_filtrado['Fecha de cierre'] >= inicio_mes) &
        (df_filtrado['Fecha de cierre'] <= hoy)
    ])

    # Promedio diario y proyección
    promedio_diario = reg_actual / dias_habiles_hasta_hoy if dias_habiles_hasta_hoy > 0 else 0
    proyeccion = reg_actual + (promedio_diario * dias_habiles_restantes)

    # Mostrar métricas
    st.metric("Avance actual (mes)", formato_miles_punto(reg_actual))
    st.metric("Promedio diario (hábil)", f"{promedio_diario:.2f}")
    st.metric("Proyección fin de mes", formato_miles_punto(int(proyeccion)))

    # Definir metas según responsable o equipo
    if seleccionado == "Todo el equipo":
        n_resp = len(responsables) - 1  # Restar la opción 'Todo el equipo'
        meta_min = 350 * n_resp
        meta_max = 850 * n_resp
    else:
        meta_min = 350
        meta_max = 850
    
    st.metric("Meta mínima", formato_miles_punto(meta_min))
    st.metric("Meta máxima", formato_miles_punto(meta_max))

    # Evaluación del ritmo
    if proyeccion >= meta_max:
        st.success("✅ Estás proyectando sobre la meta máxima del rango.")
    elif proyeccion >= meta_min:
        st.success("👍 Con el ritmo actual cumplirías al menos la meta mínima.")
    else:
        st.warning("⚠️ Al ritmo actual, no se cumpliría la meta mínima.")

    # Gráfico proyección acumulada hasta hoy (línea)
    st.caption("Proyección visual acumulada durante el mes")
    chart_data = pd.DataFrame({
        'Día hábil': list(range(1, dias_habiles_hasta_hoy + 1)),
        'Acumulado': [promedio_diario * i for i in range(1, dias_habiles_hasta_hoy + 1)]
    })
    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X('Día hábil:Q', title='Día hábil del mes'),
            y=alt.Y('Acumulado:Q', title='Regularizadas acumuladas'),
            tooltip=['Día hábil', 'Acumulado']
        )
        .properties(
            width=700,
            height=400,
            title="Avance de Regularizadas durante el mes"
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
