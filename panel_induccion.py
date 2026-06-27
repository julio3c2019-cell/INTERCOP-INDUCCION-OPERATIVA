import pandas as pd
import plotly.express as px
import streamlit as st
import os

# ----------------------
# CONFIGURACIÓN FIJA DE MARCA
# ----------------------
COLORES = {
    "fondo": "#e8f4f8",          # Fondo general celeste suave
    "texto": "#002d59",          # Texto principal en azul oscuro para buena lectura
    "acento": "#ffd000",         # Amarillo corporativo
    "detalle": "#00aeea",        # Azul celeste
    "fondo_tarjeta": "#ffffff",  # Fondo blanco para tarjetas
    "borde_tarjeta": "#bdd7e7"   # Borde suave para tarjetas
}

# ----------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ----------------------
st.set_page_config(
    page_title="INTERCOP | Inducción Operativa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 ESTILOS ACTUALIZADOS A FONDO CELESTE
st.markdown("""
<style>
#MainMenu, footer, div[data-testid="stMarkdown"] pre, div.docstring, div.stDocstring,
div.element-container:has(pre), div.block-container > div:has(pre),
div[data-testid="stMarkdown"] code, div[data-testid="stMarkdown"] div:has(.docstring) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

html, body, .stApp {
    background-color: #e8f4f8 !important;
    color: #002d59 !important;
    font-family: Arial, sans-serif !important;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #002d59 !important;
}

.stMetric {
    background: #ffffff !important;
    border-left: 5px solid #ffd000 !important;
    padding: 1rem !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

.stMetric div[data-testid="stMetricValue"] {
    color: #002d59 !important;
    font-weight: bold !important;
}

.stSidebar {
    background: #dceef5 !important;
    border-right: 2px solid #00aeea !important;
}

hr {
    border-color: #00aeea !important;
}

/* Estilo para tablas */
.stDataFrame td, .stDataFrame th {
    color: #002d59 !important;
}

/* Estilo para etiquetas de filtros */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #002d59 !important;
    color: #ffffff !important;
}
.stMultiSelect [data-baseweb="tag"] span {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# ENCABEZADO
# ----------------------
st.markdown(f"""
<div style="background:{COLORES['fondo_tarjeta']}; padding:1.5rem; border-radius:8px; border:1px solid {COLORES['borde_tarjeta']}; margin-bottom:2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <h1 style="margin:0; font-size:2.2rem; color:{COLORES['texto']};">📊 COOPERATIVA INTERCOP</h1>
    <p style="color:{COLORES['acento']}; margin:0.5rem 0 0 0; font-size:1.2rem; font-weight:500;">Panel de Control: Inducción Operativa 2026</p>
</div>
""", unsafe_allow_html=True)

# ----------------------
# CARGA DE DATOS
# ----------------------
try:
    ruta = None
    archivos = ["inducción operativa.xlsx", "induccion operativa.xlsx", "Inducción Operativa.xlsx"]
    for nombre in archivos:
        if os.path.exists(nombre):
            ruta = nombre
            break
    if not ruta:
        raise FileNotFoundError("Archivo no encontrado en la carpeta")

    df = pd.read_excel(ruta, header=None, skiprows=2)

    columnas = [
        "No.", "Mes de ingreso", "Agencia", "Nombre", "Puesto", "Fecha ingreso",
        "Encargado", "No. teléfono", "Motivo de ingreso", "Informe",
        "Nota de Desarrollo Técnico", "Nota de Operaciones", "Nota de Atención al asociado",
        "Nota total", "tipo de colaborador", "Observaciones"
    ]
    df = df.iloc[:, :len(columnas)]
    df.columns = columnas

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Cierra el archivo Excel antes de ejecutar")
    st.stop()

# ----------------------
# LIMPIEZA DE DATOS
# ----------------------
for col in ["Nota de Desarrollo Técnico", "Nota de Operaciones", "Nota de Atención al asociado", "Nota total"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Agencia"] = df["Agencia"].fillna("Sin dato").astype(str).str.strip()
df = df[df["Agencia"] != ""]

df["Puesto"] = df["Puesto"].fillna("Sin dato").astype(str).str.strip()
df["Encargado"] = df["Encargado"].fillna("Sin asignar").astype(str).str.strip()
df["tipo de colaborador"] = df["tipo de colaborador"].fillna("Sin clasificar").astype(str).str.strip()

df_valido = df[df["Nota total"].notna() & (df["Nota total"] > 0)].copy()
if df_valido.empty:
    st.warning("⚠️ No hay registros con notas válidas")
    st.stop()

# ----------------------
# FILTROS
# ----------------------
st.sidebar.header("⚙️ Filtros")
orden_meses = ["Marzo", "Abril", "Mayo", "Junio"]
meses = sorted(df_valido["Mes de ingreso"].dropna().unique(), key=lambda x: orden_meses.index(x) if x in orden_meses else 99)
meses_sel = st.sidebar.multiselect("Mes de ingreso", meses, default=meses)

agencias = sorted(df_valido["Agencia"].unique())
agencias_sel = st.sidebar.multiselect("Agencia", agencias, default=agencias)

puestos = sorted(df_valido["Puesto"].unique())
puestos_sel = st.sidebar.multiselect("Puesto", puestos, default=puestos)

tipos_colab = sorted(df_valido["tipo de colaborador"].unique())
tipos_sel = st.sidebar.multiselect("Tipo de colaborador", tipos_colab, default=tipos_colab)

encargados = sorted(df_valido["Encargado"].unique())
encargados_sel = st.sidebar.multiselect("Encargado", encargados, default=encargados)

df_filtrado = df_valido[
    df_valido["Mes de ingreso"].isin(meses_sel) &
    df_valido["Agencia"].isin(agencias_sel) &
    df_valido["Puesto"].isin(puestos_sel) &
    df_valido["tipo de colaborador"].isin(tipos_sel) &
    df_valido["Encargado"].isin(encargados_sel)
].copy()

if df_filtrado.empty:
    st.warning("⚠️ Sin datos para los filtros seleccionados")
    st.stop()

# ----------------------
# INDICADORES GENERALES
# ----------------------
def resumen(d):
    return {
        "total": len(d),
        "tecnico": round(d["Nota de Desarrollo Técnico"].mean(), 2),
        "operaciones": round(d["Nota de Operaciones"].mean(), 2),
        "atencion": round(d["Nota de Atención al asociado"].mean(), 2),
        "general": round(d["Nota total"].mean(), 2),
        "bajo": len(d[d["Nota total"] < 60]),
        "alto": len(d[d["Nota total"] >= 85])
    }

r = resumen(df_filtrado)

st.subheader(f"📊 Resumen | {r['total']} colaboradores")
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
c1.metric("Total", r["total"])
c2.metric("Promedio General", r["general"])
c3.metric("Desarrollo Técnico", r["tecnico"])
c4.metric("Operaciones", r["operaciones"])
c5.metric("Atención", r["atencion"])
c6.metric("Desempeño Bajo", r["bajo"])
c7.metric("Desempeño Alto", r["alto"])

st.divider()

# ----------------------
# TODAS LAS GRÁFICAS
# ----------------------

# 1. Promedio de nota por mes
st.subheader("📅 Promedio de Nota Total por Mes")
pm = df_filtrado.groupby("Mes de ingreso")["Nota total"].mean().round(2).reindex(orden_meses)
fig1 = px.bar(
    x=pm.index, y=pm.values, text=pm.values,
    color=pm.values, color_continuous_scale=["#ffd000", "#00aeea"],
    labels={"x": "Mes", "y": "Promedio de Nota"}
)
fig1.update_traces(textposition="outside", textfont_color="#002d59")
fig1.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="#ffffff", 
    coloraxis_showscale=False, 
    font_color="#002d59",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#e2eff5")
)
st.plotly_chart(fig1, use_container_width=True)

# 2. Desempeño promedio por área evaluada
st.subheader("📈 Desempeño Promedio por Área")
areas = ["Desarrollo Técnico", "Operaciones", "Atención al Asociado"]
valores = [r["tecnico"], r["operaciones"], r["atencion"]]
fig2 = px.bar(
    x=areas, y=valores, text=valores,
    color=valores, color_continuous_scale=["#ffd000", "#00aeea"],
    labels={"x": "Área", "y": "Promedio de Nota"}
)
fig2.update_traces(textposition="outside", textfont_color="#002d59")
fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="#ffffff", 
    coloraxis_showscale=False, 
    font_color="#002d59",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#e2eff5")
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Distribución por tipo de colaborador
st.subheader("👥 Distribución por Tipo de Colaborador")
conteo_tipo = df_filtrado["tipo de colaborador"].value_counts()
fig3 = px.pie(
    values=conteo_tipo.values, names=conteo_tipo.index, hole=0.4,
    color_discrete_sequence=["#ffd000", "#00aeea", "#e94591", "#002d59", "#80c8f0"]
)
fig3.update_traces(textinfo="percent+label", textfont_color="#002d59")
fig3.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    font_color="#002d59"
)
st.plotly_chart(fig3, use_container_width=True)

# 4. Cantidad de inducciones por encargado
st.subheader("👤 Cantidad de Inducciones por Encargado")
conteo_enc = df_filtrado["Encargado"].value_counts().sort_values(ascending=True)
fig4 = px.bar(
    y=conteo_enc.index, x=conteo_enc.values, orientation="h",
    text=conteo_enc.values, color=conteo_enc.values,
    color_continuous_scale=["#ffd000", "#00aeea"],
    labels={"y": "Encargado", "x": "Cantidad de colaboradores"}
)
fig4.update_traces(textposition="outside", textfont_color="#002d59")
fig4.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="#ffffff", 
    coloraxis_showscale=False, 
    font_color="#002d59",
    xaxis=dict(showgrid=True, gridcolor="#e2eff5"),
    yaxis=dict(showgrid=False)
)
st.plotly_chart(fig4, use_container_width=True)

# 5. Promedio de nota por agencia
st.subheader("🏢 Promedio de Nota por Agencia")
prom_agencia = df_filtrado.groupby("Agencia")["Nota total"].mean().round(2).sort_values(ascending=False)
fig5 = px.bar(
    x=prom_agencia.index, y=prom_agencia.values, text=prom_agencia.values,
    color=prom_agencia.values, color_continuous_scale=["#ffd000", "#00aeea"],
    labels={"x": "Agencia", "y": "Promedio de Nota"}
)
fig5.update_traces(textposition="outside", textfont_color="#002d59")
fig5.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="#ffffff", 
    coloraxis_showscale=False, 
    font_color="#002d59",
    xaxis=dict(showgrid=False, tickangle=-45),
    yaxis=dict(showgrid=True, gridcolor="#e2eff5")
)
st.plotly_chart(fig5, use_container_width=True)

# ----------------------
# TABLAS DE DESEMPEÑO
# ----------------------
st.subheader("⚠️ Desempeño Bajo (< 60 puntos)")
bajos = df_filtrado[df_filtrado["Nota total"] < 60][["Nombre", "Agencia", "Puesto", "Mes de ingreso", "Nota total", "Encargado", "Observaciones"]]
if not bajos.empty:
    st.dataframe(bajos, use_container_width=True)
else:
    st.success("✅ No hay registros con desempeño bajo")

st.subheader("🏆 Buen Desempeño (≥ 85 puntos)")
altos = df_filtrado[df_filtrado["Nota total"] >= 85][["Nombre", "Agencia", "Puesto", "Mes de ingreso", "Nota total", "tipo de colaborador", "Encargado"]]
if not altos.empty:
    st.dataframe(altos, use_container_width=True)
else:
    st.info("ℹ️ No hay registros con calificación mayor o igual a 85")

with st.expander("📋 Ver todos los datos completos filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)

# ----------------------
# PIE DE PÁGINA
# ----------------------
st.markdown(f"""
<hr style="border-color:{COLORES['detalle']};">
<div style="text-align:center; padding:1rem; background:{COLORES['fondo_tarjeta']}; border-radius:6px; border:1px solid {COLORES['borde_tarjeta']}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <p style="margin:0; color:{COLORES['texto']};">© 2026 Cooperativa INTERCOP | Todos los derechos reservados</p>
    <p style="color:{COLORES['acento']}; margin:0.5rem 0 0 0; font-weight:500;">Solidez e Innovación al servicio de nuestros asociados</p>
</div>
""", unsafe_allow_html=True)
