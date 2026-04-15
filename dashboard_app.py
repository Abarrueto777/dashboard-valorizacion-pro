import streamlit as st
import pandas as pd

# CONFIG
st.set_page_config(page_title="Dashboard Dinámico", layout="wide")

st.title("📊 Dashboard Dinámico de Datos")

# SUBIR ARCHIVO
archivo = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if not archivo:
    st.warning("Sube un archivo para comenzar")
    st.stop()

df = pd.read_excel(archivo)

st.sidebar.markdown("### 🧩 Configuración de columnas")

columnas = df.columns.tolist()

# MAPEO DINÁMICO
fecha_col = st.sidebar.selectbox("Columna de Fecha", columnas)
categoria_col = st.sidebar.selectbox("Categoría (ej: comuna)", columnas)
segmento_col = st.sidebar.selectbox("Segmento (ej: valorizador)", columnas)

# LIMPIEZA DE FECHA
df[fecha_col] = pd.to_datetime(df[fecha_col], dayfirst=True, errors="coerce")
df = df.dropna(subset=[fecha_col])

# FILTRO FECHA
st.sidebar.markdown("### 📅 Filtro de fecha")

fecha_min = df[fecha_col].min()
fecha_max = df[fecha_col].max()

rango = st.sidebar.date_input("Rango", [fecha_min, fecha_max])

filtered = df.copy()

if len(rango) == 2:
    inicio = pd.to_datetime(rango[0])
    fin = pd.to_datetime(rango[1]) + pd.Timedelta(days=1)

    filtered = filtered[
        (filtered[fecha_col] >= inicio) &
        (filtered[fecha_col] < fin)
    ]

# KPIs
st.markdown("### 📌 Indicadores")

col1, col2, col3 = st.columns(3)

total = len(filtered)
categorias = filtered[categoria_col].nunique()
segmentos = filtered[segmento_col].nunique()

col1.metric("Total registros", total)
col2.metric("Categorías", categorias)
col3.metric("Segmentos", segmentos)

# EVOLUCIÓN
st.markdown("### ⏳ Evolución")

tipo = st.radio("Vista", ["Diaria", "Mensual"], horizontal=True)

df_time = filtered.copy().set_index(fecha_col)

if tipo == "Diaria":
    evolucion = df_time.resample("D").size().reset_index()
    evolucion["Fecha"] = evolucion[fecha_col].dt.strftime("%d-%m-%Y")
else:
    evolucion = df_time.resample("MS").size().reset_index()
    evolucion["Fecha"] = evolucion[fecha_col].dt.strftime("%m-%Y")

evolucion.columns = ["Fecha original", "Cantidad", "Fecha"]

st.line_chart(evolucion.set_index("Fecha")["Cantidad"])

# GRÁFICOS
st.markdown("### 📈 Distribución")

col1, col2 = st.columns(2)

with col1:
    st.write("Por categoría")
    st.bar_chart(filtered[categoria_col].value_counts())

with col2:
    st.write("Por segmento")
    st.bar_chart(filtered[segmento_col].value_counts())

# CRUCE (MUY PRO 🔥)
st.markdown("### 🔄 Cruce de variables")

cruce = pd.crosstab(filtered[categoria_col], filtered[segmento_col])
st.dataframe(cruce)

# EXPORTAR
st.markdown("### 📤 Exportar")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Descargar datos filtrados",
    csv,
    "datos_filtrados.csv",
    "text/csv"
)

# TABLA FINAL
st.markdown("### 📄 Datos")

tabla = filtered.copy()
tabla[fecha_col] = tabla[fecha_col].dt.strftime("%d-%m-%Y")

st.dataframe(tabla, use_container_width=True)
