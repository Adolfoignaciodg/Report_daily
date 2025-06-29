# 📊 Dashboard Operacional – Visualizador de Producción Interna

Este proyecto es una **herramienta interactiva de visualización de datos operacionales**, creada con [Streamlit](https://streamlit.io/). Nació como una solución personal para monitorear el avance, estado y calidad de los procesos internos de una operación real, pero usando **datos simulados y anonimizados** para fines de desarrollo y demostración.

> 💡 Ideal para equipos que gestionan operaciones masivas, necesitan controlar el stock de casos pendientes, tiempos de resolución y desempeño por trabajador.

---

## 🧠 ¿Qué hace esta aplicación?

- 📌 Muestra un **resumen general** del stock total por tipo de error (20 o 28), operaciones regularizadas y su desglose por tipo de programa (COVID, Chile Apoya, etc.).
- 📈 Permite analizar la **producción mensual**, con métricas por tipo de error y un detalle por día del mes seleccionado.
- 👤 Visualiza el **desempeño individual** de cada trabajador, destacando casos regularizados, pendientes, atrasados y otros estados operativos.
- 📊 Incluye gráficos interactivos que comparan la producción **mes a mes** a lo largo de varios años.

---

## 📁 Sobre los datos (archivo: `reporte.xlsx`)

Este archivo contiene datos **ficticios** con la misma estructura que una operación real, pero sin ninguna información personal ni sensible. Cumple con buenas prácticas de anonimización.

| Campo                            | Incluido | Sensible | Descripción breve                                 |
|----------------------------------|----------|----------|----------------------------------------------------|
| CUI / Operación banco / RUT     | ❌       | ✅       | Eliminados por privacidad.                         |
| Responsable                     | ✅       | Baja     | Se incluyen solo nombres, sin apellidos.           |
| FECHA / Fecha de cierre         | ✅       | No       | Permiten el análisis temporal de gestión.          |
| PROGRAMA / TIPO ERROR           | ✅       | No       | Clasificación interna de las operaciones.          |
| ESTADO FINAL / Observaciones    | ✅       | No       | Estado actual y contexto funcional.                |
| Otros campos operativos         | ✅       | No       | Agregados útiles para el análisis y seguimiento.   |

---

## 🛠️ Requisitos previos

Antes de comenzar, asegúrate de tener:
```
- Python 3.10 o superior
- pip (administrador de paquetes de Python)
- Git (opcional, para clonar el repositorio)
```

---

## 🚀 Cómo ejecutar el proyecto paso a paso

### 1. Clona el repositorio (opcional)

Si usas Git:

```
git clone https://github.com/tu-usuario/dashboard-operacional.git
cd dashboard-operacional
```

---

### 2. Instala las dependencias
Ejecuta este comando en la carpeta donde tienes el proyecto:
```
pip install -r requirements.txt

```
📦 Esto instalará:

streamlit: para la interfaz web.

pandas: para manipulación de datos.

altair: para gráficos interactivos.

openpyxl: para leer archivos Excel.

---
### 3. Ejecuta la aplicación

```
streamlit run dashboard.py
Esto abrirá una ventana en tu navegador con el dashboard interactivo.
```

🧭 ¿Cómo usar la app?


📌 Menú lateral


Al abrir la app, verás un menú lateral con tres vistas disponibles:

#### ① Resumen General

- Carga el Excel actualizado (o usa uno por defecto).
- Muestra el total de operaciones, tipo de error, regularizadas.
- Desglose de operaciones regularizadas por tipo de programa.
- Tabla y gráfico por colaborador.

#### ② Producción Total Mensual

- Selecciona un mes y año.
- Visualiza las operaciones regularizadas en ese período.
- Desglose diario por tipo de error.
- Gráfica de producción mensual.

#### ③ Detalle por Trabajador

- Selecciona un nombre.
- Muestra sus operaciones por estado: regularizadas, en revisión, pendientes, atrasadas y otros.
- Gráfico mensual de su producción histórica.
- Tablas específicas de atrasos y otros estados.


📸 Ejemplo de visualización

```
<img src="https://user-images.githubusercontent.com/..." alt="Vista ejemplo del dashboard" width="700">
⚠️ Imagen referencial. Los datos y nombres en la demo son completamente ficticios.
 ```

📚 Estructura del repositorio


```

📂 dashboard-operacional/
│
├── dashboard.py                # Script principal con la app en Streamlit
├── reportes.xlsx               # Archivo Excel con datos simulados
├── requirements.txt            # Lista de dependencias
└── README.md                   # Este documento

```

🔐 Consideraciones de privacidad


```
Todos los datos reales fueron anonimizados o eliminados antes de ser utilizados en esta demo.
El proyecto cumple con prácticas básicas de protección de datos.
```

🧱 Posibles mejoras futuras

```
(...)

```


---


