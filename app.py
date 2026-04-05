"""
CitizenWatch Pro — Plataforma de Inteligencia Ciudadana España
Datos OSINT + Fuentes Oficiales: INE, CIS, Interior, Transparencia, BOE
Miguel Castillo / SIEG — Odroid C2 / DietPi
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Paths ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
import sys as _sys
_sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    import mapa_ccaa as mc
    HAS_MAPA = True
except Exception:
    HAS_MAPA = False
DB_PATH  = BASE_DIR / "data" / "citizen_data.db"
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Config página — SEO real ─────────────────────────────────
st.set_page_config(
    page_title="CitizenWatch Pro | Auditoría Ciudadana España 2026",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "CitizenWatch Pro — Plataforma independiente de inteligencia ciudadana. "
            "Datos: INE, CIS, Ministerio del Interior, Portal de Transparencia, BOE. "
            "Metodología OSINT aplicada a la realidad social española."
        )
    }
)

# ── SEO meta injection ───────────────────────────────────────
st.markdown("""
<head>
<meta name="description" content="CitizenWatch Pro: auditoría ciudadana independiente de España. 
Datos reales sobre paro, inseguridad, corrupción política, vivienda, sanidad, inmigración y educación. 
Fuentes: INE, CIS, Ministerio del Interior, Transparencia, BOE."/>
<meta name="keywords" content="auditoría ciudadana España, paro España 2026, inseguridad ciudadana, 
corrupción política España, vivienda alquiler crisis, sanidad pública listas espera, 
inmigración estadísticas, gasto político España, OSINT España, transparencia pública"/>
<meta name="author" content="CitizenWatch Pro / SIEG"/>
<meta property="og:title" content="CitizenWatch Pro | Auditoría Ciudadana España 2026"/>
<meta property="og:description" content="Plataforma OSINT independiente. Datos reales sobre las 
principales preocupaciones de los españoles."/>
<meta property="og:type" content="website"/>
</head>
""", unsafe_allow_html=True)

# ── Tema visual ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg:      #0d1117;
    --bg2:     #161b22;
    --border:  #30363d;
    --green:   #3fb950;
    --red:     #f85149;
    --yellow:  #d29922;
    --blue:    #58a6ff;
    --orange:  #f0883e;
    --text:    #c9d1d9;
    --dim:     #8b949e;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
h1,h2,h3 { color: white !important; font-family: 'Inter', sans-serif !important; }

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.5rem !important; color: white !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important; color: var(--dim) !important;
    text-transform: uppercase !important; letter-spacing: 1.5px !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.78rem !important; letter-spacing: 1px !important;
    color: var(--dim) !important;
}
.stTabs [aria-selected="true"] { color: var(--blue) !important; }
.kpi-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px 20px; margin-bottom: 8px;
}
.kpi-card.alerta { border-left: 3px solid var(--red); }
.kpi-card.warning { border-left: 3px solid var(--yellow); }
.kpi-card.ok { border-left: 3px solid var(--green); }
.fuente-tag {
    font-size: 0.72rem; color: var(--dim);
    font-family: 'JetBrains Mono', monospace;
    background: var(--bg); padding: 2px 8px;
    border-radius: 4px; border: 1px solid var(--border);
    display: inline-block; margin: 2px;
}
.section-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px; margin-bottom: 16px;
    font-size: 0.7rem; color: var(--dim);
    text-transform: uppercase; letter-spacing: 2px;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ligero para Odroid ─────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c9d1d9", family="Inter", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
)
_AX = dict(gridcolor="#21262d", showgrid=True, zeroline=False)

# ── DB helper — ligero, sin cargar todo en memoria ───────────
STATIC_DIR = BASE_DIR / "data" / "static"

@st.cache_data(ttl=3600, show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    # Intentar SQLite primero (local/Odroid)
    try:
        if DB_PATH.exists():
            conn = sqlite3.connect(str(DB_PATH))
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df
    except Exception:
        pass
    # Fallback: CSV estáticos (Streamlit Cloud)
    import re
    m = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
    if m:
        tabla = m.group(1)
        csv_path = STATIC_DIR / f"{tabla}.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
    return pd.DataFrame()

def fuentes(*nombres):
    tags = " ".join(f'<span class="fuente-tag">{n}</span>' for n in nombres)
    st.markdown(f'<div style="margin:4px 0 12px">{tags}</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛡️ CitizenWatch Pro")
    st.markdown("<div class='section-header'>Inteligencia Ciudadana · España 2026</div>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size:0.75rem;color:#8b949e;font-family:JetBrains Mono'>
    🖥️ Nodo: Odroid C2 / DietPi<br>
    📡 Fuentes: INE · CIS · Interior · BOE<br>
    🔄 Actualización: Diaria (cron 06:00)<br>
    📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='font-size:0.72rem;color:#8b949e'>
    <b style='color:#c9d1d9'>Metodología OSINT:</b><br>
    Datos públicos oficiales procesados
    automáticamente. Sin editoriales,
    sin sesgos políticos.<br><br>
    <b style='color:#c9d1d9'>Licencia:</b> Datos abiertos CC-BY<br>
    <b style='color:#c9d1d9'>Código:</b>
    <a href='https://github.com/mcasrom' style='color:#58a6ff'>github.com/mcasrom</a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    if st.button("🔄 Actualizar datos", type="secondary"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.markdown("""
    <div style='text-align:center;padding:8px 0'>
        <a href='https://ko-fi.com/mcasrom' target='_blank'
           style='background:#FF5E5B;color:white;padding:8px 16px;
           border-radius:6px;text-decoration:none;font-size:0.8rem;
           font-weight:600;display:inline-block'>
            ☕ Apóyame en Ko-fi
        </a>
    </div>
    <div style='font-size:0.68rem;color:#8b949e;text-align:center;margin-top:8px'>
        © 2026 M. Castillo<br>
        <a href='mailto:mybloggingnotes@gmail.com'
           style='color:#58a6ff'>mybloggingnotes@gmail.com</a><br>
        <a href='https://github.com/mcasrom/dashboard_citizen'
           style='color:#58a6ff'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<h1 style='margin-bottom:4px'>🛡️ CitizenWatch Pro</h1>
<p style='color:#8b949e;font-size:0.9rem;margin-bottom:0'>
Plataforma independiente de auditoría ciudadana — España 2026 · 
Datos: INE · CIS · Ministerio del Interior · Portal de Transparencia · BOE
</p>
""", unsafe_allow_html=True)

# ── KPIs globales — fila superior ───────────────────────────
st.markdown("---")
df_tension = query("SELECT * FROM tension_social")
df_trabajo = query("SELECT * FROM trabajo_split")
df_cis     = query("SELECT * FROM cis_tension ORDER BY preocupacion DESC LIMIT 1")
df_inm     = query("SELECT * FROM inmigracion_stats LIMIT 1")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🏠 Crisis Vivienda",  "42.1%",  "+8.2% anual",
          help="% salario medio destinado a alquiler. Fuente: CIS / Idealista")
c2.metric("💼 Paro Juvenil",     "27.4%",  "+1.2%",
          help="Tasa desempleo <25 años. Fuente: EPA/INE")
c3.metric("🚨 Inseguridad",      "15.2%",  "+3.1%",
          help="% ciudadanos que señalan inseguridad como problema. Fuente: CIS")
c4.metric("🏛️ Desafección",      "34.2%",  "Máximo",
          help="% que señala mal comportamiento político como problema. Fuente: CIS")
c5.metric("🌍 Preoc. Inmigración","32.5%", "+4.0%",
          help="% que señala inmigración entre sus 3 principales problemas. Fuente: CIS")
c6.metric("🏥 Listas Espera",    "787k",   "+12% anual",
          help="Pacientes en lista de espera quirúrgica. Fuente: SNS/Ministerio Sanidad")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Barómetro Social",
    "💼 Empleo",
    "🏠 Vivienda",
    "🚨 Seguridad",
    "🏛️ Gasto Político",
    "🌍 Inmigración",
    "🏥 Sanidad",
    "⚖️ Corrupción & PGE",
    "🌐 Geopolítica",
    "🗺️ Mapas CCAA",
    "🔬 Metodología",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — BARÓMETRO SOCIAL
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("#### 📊 Principales preocupaciones de los españoles")
    fuentes("CIS Barómetro mensual", "Encuesta Condiciones de Vida INE",
            "Eurobarómetro")

    df_cis_full = query("SELECT * FROM cis_tension ORDER BY preocupacion DESC")
    df_bar_hist = query("SELECT * FROM cis_barometro ORDER BY año, problema")

    if not df_cis_full.empty:
        col1, col2 = st.columns([3, 2])
        with col1:
            colores = ["#f85149" if p > 25 else "#d29922" if p > 15 else "#3fb950"
                       for p in df_cis_full["preocupacion"]]
            fig = go.Figure(go.Bar(
                x=df_cis_full["preocupacion"],
                y=df_cis_full["problema"],
                orientation="h",
                marker_color=colores,
                text=[f"{v:.1f}%" for v in df_cis_full["preocupacion"]],
                textposition="outside",
            ))
            fig.update_layout(**PLOT, height=320,
                              title="% ciudadanos que lo señalan como problema principal",
                              xaxis=dict(gridcolor="#21262d", range=[0, 45]))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            for _, r in df_cis_full.iterrows():
                css = "alerta" if r["preocupacion"] > 25 else \
                      "warning" if r["preocupacion"] > 15 else "ok"
                icon = "🔴" if css == "alerta" else "🟡" if css == "warning" else "🟢"
                st.markdown(f"""
                <div class='kpi-card {css}'>
                    <b>{icon} {r['problema']}</b><br>
                    <span style='font-size:1.3rem;font-family:JetBrains Mono;
                    color:white'>{r['preocupacion']:.1f}%</span><br>
                    <span style='font-size:0.75rem;color:#8b949e'>{r['tendencia']}</span>
                </div>
                """, unsafe_allow_html=True)

    # Evolución histórica CIS
    if not df_bar_hist.empty:
        st.markdown("#### Evolución anual — Principales problemas")
        fig2 = px.line(df_bar_hist, x="año", y="porcentaje",
                       color="problema", markers=True,
                       color_discrete_sequence=["#58a6ff","#f85149","#3fb950",
                                                 "#d29922","#f0883e","#bc8cff"])
        fig2.update_layout(**PLOT, height=280)
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — EMPLEO
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("#### 💼 Mercado laboral — Estructura y precariedad")
    fuentes("EPA / INE (trimestral)", "Ministerio de Trabajo",
            "SEPE — Estadística paro registrado")

    df_trab = query("SELECT * FROM trabajo_split")
    df_inq  = query("SELECT * FROM inquietudes_historico WHERE categoria='Empleo'")

    if not df_trab.empty:
        col1, col2, col3 = st.columns(3)
        for i, (_, r) in enumerate(df_trab.iterrows()):
            col = [col1, col2, col3][i % 3]
            with col:
                st.markdown(f"""
                <div class='kpi-card alerta'>
                    <div style='font-size:0.72rem;color:#8b949e;
                    text-transform:uppercase;letter-spacing:1px'>{r.iloc[0]}</div>
                    <div style='font-size:1.4rem;font-family:JetBrains Mono;
                    color:white;margin:4px 0'>{r.iloc[1]}%</div>
                    <div style='font-size:0.75rem;color:#f85149'>{r.iloc[2]}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Distribución del empleo por tipo de contrato")
    fig_emp = go.Figure(go.Pie(
        labels=["Indefinido", "Temporal <6m", "Autónomo precario",
                "Subempleo cualificado", "Interino público"],
        values=[38, 32, 12, 35, 31],
        hole=0.45,
        marker_colors=["#3fb950","#f85149","#d29922","#f0883e","#58a6ff"],
    ))
    fig_emp.update_layout(**PLOT, height=300,
                          title="% sobre población activa (estimación EPA)")
    st.plotly_chart(fig_emp, use_container_width=True)

    st.info("📌 **Dato clave:** El 35.8% de los graduados universitarios trabaja en "
            "empleos que no requieren su titulación (INE, Encuesta Inserción Laboral 2025).")

# ══════════════════════════════════════════════════════════════
# TAB 3 — VIVIENDA
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("#### 🏠 Crisis de vivienda — Accesibilidad y precios")
    fuentes("Banco de España", "INE — Estadística Hipotecas",
            "Idealista / Fotocasa", "CIS Barómetro")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Esfuerzo alquiler",  "42.1%", "+8.2%",
                help="% salario bruto medio destinado a alquiler. Máximo histórico.")
    col2.metric("Precio €/m² Madrid", "21.4€",  "+14%",
                help="Precio medio alquiler Madrid capital. Fuente: Idealista Q1 2026")
    col3.metric("Hipoteca vs salario", "33.8%", "+5.1%",
                help="Esfuerzo hipotecario sobre salario neto medio.")
    col4.metric("Jóvenes emancipados", "18.3%", "-2.1%",
                help="% jóvenes 18-29 con vivienda independiente. Mínimo UE.")

    # Evolución precios por ciudad
    ciudades = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga"]
    precios_2023 = [17.2, 16.8, 11.2, 9.8, 12.1, 13.4]
    precios_2025 = [21.4, 20.1, 14.8, 12.3, 14.2, 17.8]

    fig_viv = go.Figure()
    fig_viv.add_trace(go.Bar(name="2023", x=ciudades, y=precios_2023,
                              marker_color="#58a6ff"))
    fig_viv.add_trace(go.Bar(name="2025", x=ciudades, y=precios_2025,
                              marker_color="#f85149"))
    fig_viv.update_layout(**PLOT, barmode="group", height=300,
                           title="Precio alquiler €/m² por ciudad",
                           yaxis=dict(gridcolor="#21262d", title="€/m²"))
    st.plotly_chart(fig_viv, use_container_width=True)

    st.error("⚠️ España tiene el **ratio vivienda/salario más alto de la UE** para menores "
             "de 35 años. El acceso a primera vivienda requiere de media 7.2 años de "
             "ahorro íntegro del salario bruto. (Banco de España, 2025)")

# ══════════════════════════════════════════════════════════════
# TAB 4 — SEGURIDAD
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("#### 🚨 Seguridad ciudadana — Criminalidad y percepción")
    fuentes("Ministerio del Interior — Anuario Estadístico",
            "Fiscalía General del Estado", "CIS — Percepción inseguridad")

    df_crime = query("SELECT * FROM criminalidad_detallada")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Infracciones penales", "2.1M", "+8.4%",
                help="Total infracciones penales conocidas. Fuente: Interior 2025")
    col2.metric("Delitos informáticos", "+24%", "Tendencia",
                help="Ciberestafas, phishing, sextorsión. Mayor crecimiento delictivo.")
    col3.metric("Reincidencia penal",   "42%",  "Estructural",
                help="% penados que reingresan en 3 años. Fuente: SGIP")
    col4.metric("Percepción inseguridad","15.2%","+3.1%",
                help="% que señala inseguridad entre sus 3 problemas. CIS 2025")

    if not df_crime.empty:
        st.markdown("#### Tipología delictiva — Tendencias 2025")
        fig_crime = go.Figure(go.Bar(
            x=df_crime.iloc[:, 1].astype(float),
            y=df_crime.iloc[:, 0],
            orientation="h",
            marker_color="#f0883e",
            text=[f"{v:.1f}" for v in df_crime.iloc[:, 1].astype(float)],
            textposition="outside",
        ))
        fig_crime.update_layout(**PLOT, height=280,
                                 xaxis=dict(gridcolor="#21262d", title="Índice / %"))
        st.plotly_chart(fig_crime, use_container_width=True)

    st.markdown("#### Contexto europeo")
    paises = ["España", "Francia", "Alemania", "Italia", "UE Media"]
    indices = [15.2, 18.4, 12.1, 22.3, 16.8]
    fig_eu = go.Figure(go.Bar(
        x=paises, y=indices,
        marker_color=["#f85149","#d29922","#3fb950","#f85149","#58a6ff"],
        text=[f"{v}%" for v in indices], textposition="outside",
    ))
    fig_eu.update_layout(**PLOT, height=260,
                          title="Percepción inseguridad ciudadana — comparativa UE (%)",
                          yaxis=dict(gridcolor="#21262d", range=[0, 30]))
    st.plotly_chart(fig_eu, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — GASTO POLÍTICO
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### 🏛️ Gasto político y corrupción — Auditoría pública")
    fuentes("Portal de Transparencia", "BOE", "Tribunal de Cuentas",
            "Transparencia Internacional — IPC")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cargos de confianza",  "1.100M€", "+12%",
                help="Gasto en asesores y personal de confianza. Récord histórico.")
    col2.metric("Publicidad institucional","600M€", "+8%",
                help="Gasto en publicidad y comunicación institucional.")
    col3.metric("Índice Corrupción CPI", "58/100", "-2pts",
                help="Índice Percepción Corrupción. España puesto 36 mundial. TI 2025")
    col4.metric("Causas penales activas", "1.847", "+134",
                help="Causas por corrupción pública activas en tribunales. Fuente: CGPJ")

    df_gasto = query("SELECT * FROM gasto_detallado ORDER BY cantidad DESC")
    df_corrup = query("SELECT * FROM gasto_corrupcion LIMIT 10")

    if not df_gasto.empty:
        st.markdown("#### Distribución presupuesto por área (M€)")
        try:
            areas = df_gasto.groupby("area")["cantidad"].sum().reset_index()
            fig_g = go.Figure(go.Treemap(
                labels=areas["area"],
                parents=[""] * len(areas),
                values=areas["cantidad"],
                textinfo="label+value",
                marker_colorscale="RdYlGn",
            ))
            fig_g.update_layout(**PLOT, height=320)
            st.plotly_chart(fig_g, use_container_width=True)
        except Exception:
            st.dataframe(df_gasto, use_container_width=True, hide_index=True)

    st.markdown("#### Comparativa: Gasto social vs Gasto político (M€)")
    df_vs = query("SELECT * FROM gasto_politico_vs_social")
    if not df_vs.empty:
        st.dataframe(df_vs, use_container_width=True, hide_index=True)
    else:
        comparativa = {
            "Concepto": ["Sanidad pública", "Educación pública",
                         "Cargos de confianza", "Publicidad institucional",
                         "Subvenciones a partidos", "Alta velocidad (AVE)"],
            "Millones €": [75400, 52000, 1100, 600, 300, 6200],
            "Variación": ["+3.1%", "+2.8%", "+12%", "+8%", "+5%", "+18%"],
        }
        st.dataframe(pd.DataFrame(comparativa),
                     use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — INMIGRACIÓN
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("#### 🌍 Inmigración — Datos y percepción social")
    fuentes("INE — Padrón Municipal", "Ministerio del Interior",
            "Eurostat", "CIS Barómetro")

    df_inm = query("SELECT * FROM inmigracion_stats")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Población extranjera", "6.54M",  "+380k",
                help="Total extranjeros empadronados. 13.1% población. INE 2025")
    col2.metric("Solicitudes asilo",    "163k",   "+22%",
                help="Solicitudes de protección internacional. Ministerio Interior 2025")
    col3.metric("Preocupación CIS",     "32.5%",  "+4pts",
                help="% que señala inmigración entre sus 3 principales problemas.")
    col4.metric("Menores no acompañados","6.800", "+1.200",
                help="MENAs en sistemas de protección. Ministerio Derechos Sociales.")

    if not df_inm.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Origen de la población extranjera")
            fig_inm = go.Figure(go.Bar(
                x=df_inm.iloc[:, 1].astype(float),
                y=df_inm.iloc[:, 0],
                orientation="h",
                marker_color="#58a6ff",
                text=[f"{v:.1f}%" for v in df_inm.iloc[:, 1].astype(float)],
                textposition="outside",
            ))
            fig_inm.update_layout(**PLOT, height=280)
            st.plotly_chart(fig_inm, use_container_width=True)

        with col2:
            st.markdown("#### Evolución población extranjera (millones)")
            años = [2015, 2017, 2019, 2021, 2023, 2025]
            pob  = [4.73, 4.57, 5.03, 5.43, 6.01, 6.54]
            fig_ev = go.Figure(go.Scatter(
                x=años, y=pob, mode="lines+markers",
                line=dict(color="#58a6ff", width=2),
                fill="tozeroy", fillcolor="rgba(88,166,255,0.1)",
            ))
            fig_ev.update_layout(**PLOT, height=280,
                                  yaxis=dict(gridcolor="#21262d", title="Millones"))
            st.plotly_chart(fig_ev, use_container_width=True)

    st.info("📌 España es el **3er país de la UE** en solicitudes de asilo (2025). "
            "El 45.2% de los extranjeros procede de Iberoamérica. (INE/Eurostat)")

# ══════════════════════════════════════════════════════════════
# TAB 7 — SANIDAD
# ══════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("#### 🏥 Sanidad pública — Listas de espera y recursos")
    fuentes("SNS — Sistema Nacional de Salud",
            "Ministerio de Sanidad", "FADSP", "Eurostat Health")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lista espera quirúrgica", "787k",  "+12%",
                help="Pacientes en espera quirúrgica. SNS junio 2025")
    col2.metric("Espera media cirugía",    "124 días", "+18d",
                help="Días medios espera intervención. SNS 2025")
    col3.metric("Médicos/1.000 hab.",      "4.1",   "-0.2",
                help="Ratio médicos por habitante. Por debajo media OCDE (3.7)")
    col4.metric("Gasto salud mental",      "< 5%",  "Crítico",
                help="% presupuesto sanitario destinado a salud mental. OCDE media: 12%")

    especialidades = ["Traumatología", "Oftalmología", "Neurología",
                      "Cardiología", "Dermatología", "Ginecología"]
    esperas = [187, 156, 134, 98, 89, 76]
    fig_san = go.Figure(go.Bar(
        x=especialidades, y=esperas,
        marker_color=["#f85149" if e > 150 else "#d29922" if e > 100 else "#3fb950"
                      for e in esperas],
        text=[f"{e}d" for e in esperas], textposition="outside",
    ))
    fig_san.update_layout(**PLOT, height=300,
                           title="Días medios de espera por especialidad (SNS 2025)",
                           yaxis=dict(gridcolor="#21262d", title="Días", range=[0, 220]))
    st.plotly_chart(fig_san, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        paises_san = ["España", "Alemania", "Francia", "Italia", "UE Media"]
        gasto_san  = [7.6, 12.8, 11.2, 9.1, 9.8]
        fig_gsan = go.Figure(go.Bar(
            x=paises_san, y=gasto_san,
            marker_color=["#f85149","#3fb950","#3fb950","#d29922","#58a6ff"],
            text=[f"{v}%" for v in gasto_san], textposition="outside",
        ))
        fig_gsan.update_layout(**PLOT, height=260,
                                title="Gasto sanitario / PIB (%)",
                                yaxis=dict(gridcolor="#21262d", range=[0, 15]))
        st.plotly_chart(fig_gsan, use_container_width=True)
    with col2:
        st.error("🔴 **Salud Mental:** España destina menos del 5% del presupuesto "
                 "sanitario a salud mental. La media OCDE es del 12%. "
                 "Lista de espera para psiquiatría: 6-18 meses en CCAA.")
        st.warning("🟡 **Atención Primaria:** 1 de cada 4 centros de salud en España "
                   "tiene déficit de médicos de familia. "
                   "Jubilaciones masivas previstas 2026-2030.")

# ══════════════════════════════════════════════════════════════
# TAB 8 — METODOLOGÍA
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# TAB 8 — CORRUPCIÓN & PGE
# ══════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("#### ⚖️ Corrupción política y Presupuestos Generales del Estado")
    fuentes("Tribunal de Cuentas", "Portal Transparencia", "BOE",
            "Transparencia Internacional — IPC", "CGPJ")

    df_pol  = query("SELECT * FROM political_perception")
    df_pge  = query("SELECT * FROM pge_split ORDER BY cantidad DESC")
    df_pgea = query("SELECT * FROM pge_audit ORDER BY cantidad DESC LIMIT 12")

    # KPIs corrupción
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Índice Corrupción CPI", "58/100", "-2pts",
                help="Transparencia Internacional 2025. Escala 0=muy corrupto, 100=muy limpio")
    col2.metric("Causas penales activas", "1.847", "+134",
                help="Causas por corrupción pública en tribunales. CGPJ 2025")
    col3.metric("Fondos públicos malversados", "3.200M€", "estimado",
                help="Estimación Tribunal de Cuentas — casos activos")
    col4.metric("Desafección política", "34.2%", "Máximo histórico",
                help="% que señala mal comportamiento político como problema. CIS 2025")

    # Percepción política
    if not df_pol.empty:
        st.markdown("#### Percepción ciudadana — Problemas políticos (CIS)")
        colores_pol = ["#f85149" if float(str(r.iloc[1]).replace(",",".")) > 25
                       else "#d29922" if float(str(r.iloc[1]).replace(",",".")) > 15
                       else "#3fb950" for _, r in df_pol.iterrows()]
        fig_pol = go.Figure(go.Bar(
            x=[float(str(r.iloc[1]).replace(",",".")) for _, r in df_pol.iterrows()],
            y=[r.iloc[0] for _, r in df_pol.iterrows()],
            orientation="h",
            marker_color=colores_pol,
            text=[f"{float(str(r.iloc[1]).replace(',','.')):,.1f}%" for _, r in df_pol.iterrows()],
            textposition="outside",
        ))
        fig_pol.update_layout(**PLOT, height=240,
                               title="% ciudadanos que lo señalan como problema (CIS 2025)")
        st.plotly_chart(fig_pol, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Presupuestos Generales del Estado — Distribución real vs presupuestado")

    col1, col2 = st.columns(2)
    with col1:
        if not df_pge.empty:
            try:
                fig_pge = go.Figure(go.Treemap(
                    labels=[f"{r.iloc[0]}\n{r.iloc[1]}" for _, r in df_pge.iterrows()],
                    parents=[""] * len(df_pge),
                    values=df_pge.iloc[:, 2].astype(float),
                    textinfo="label+value",
                    marker_colorscale="RdYlGn",
                ))
                fig_pge.update_layout(**PLOT, height=340,
                                       title="PGE por área (M€)")
                st.plotly_chart(fig_pge, use_container_width=True)
            except Exception:
                st.dataframe(df_pge, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos PGE en DB")

    with col2:
        if not df_pgea.empty:
            st.markdown("**Ejecución presupuestaria por partida**")
            for _, r in df_pgea.iterrows():
                try:
                    area   = r.iloc[0]
                    sub    = r.iloc[1]
                    cant   = float(r.iloc[2])
                    nota   = r.iloc[3] if len(r) > 3 else ""
                    css    = "alerta" if "Crítico" in str(nota) or "Insuficiente" in str(nota)                              else "warning" if "Infra" in str(nota) else "ok"
                    st.markdown(f"""
                    <div class='kpi-card {css}' style='padding:10px 14px;margin-bottom:6px'>
                        <div style='font-size:0.7rem;color:#8b949e'>{area} › {sub}</div>
                        <div style='font-size:1.1rem;font-family:JetBrains Mono;color:white'>
                            {cant:,.0f}M€</div>
                        <div style='font-size:0.72rem;color:#f85149'>{nota}</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    pass
        else:
            st.info("Sin datos de auditoría PGE en DB")

    st.error("⚠️ **Dato clave:** España ocupa el puesto 36 en el Índice de Percepción "
             "de la Corrupción (Transparencia Internacional 2025). Los escándalos de "
             "corrupción han costado al erario público más de 90.000M€ en la última década "
             "según estimaciones del Consejo de Europa.")

# ══════════════════════════════════════════════════════════════
# TAB 9 — GEOPOLÍTICA
# ══════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("#### 🌐 Geopolítica — OTAN, Mercosur, IPC y posicionamiento exterior")
    fuentes("Ministerio de Asuntos Exteriores", "CIS Barómetro",
            "INE — IPC", "Comisión Europea", "OCDE")

    df_mer = query("SELECT * FROM mercosur_impact")
    df_cis = query("SELECT * FROM cis_full ORDER BY porcentaje DESC")

    # KPIs geopolítica
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gasto defensa / PIB", "2.1%",  "+0.6%",
                help="Compromiso OTAN: 2% PIB. España alcanzó el objetivo en 2025.")
    col2.metric("IPC acumulado 2023-25", "+18.4%", "Impacto real",
                help="Inflación acumulada en bienes básicos. INE. Salarios: +9.2%")
    col3.metric("Apoyo OTAN ciudadanos", "52%",  "-8pts",
                help="% ciudadanos que apoyan la membresía en OTAN. CIS 2025")
    col4.metric("Rechazo Mercosur", "61%", "Mayoría",
                help="% ciudadanos contrarios al acuerdo UE-Mercosur. Eurobarómetro 2025")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Acuerdo UE-Mercosur — Riesgos alimentarios detectados")
        if not df_mer.empty:
            for _, r in df_mer.iterrows():
                try:
                    producto  = r.iloc[0]
                    categoria = r.iloc[1]
                    riesgo    = r.iloc[2]
                    impacto   = r.iloc[3] if len(r) > 3 else ""
                    st.markdown(f"""
                    <div class='kpi-card alerta' style='padding:10px 14px;margin-bottom:6px'>
                        <div style='font-size:0.85rem;font-weight:600;color:white'>
                            🥩 {producto}</div>
                        <div style='font-size:0.75rem;color:#d29922'>{categoria} · {riesgo}</div>
                        <div style='font-size:0.72rem;color:#f85149'>{impacto}</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    pass
        else:
            st.warning("Sin datos Mercosur en DB")

    with col2:
        st.markdown("#### Opinión ciudadana — Principales problemas 2025 (CIS Full)")
        if not df_cis.empty:
            fig_cis = go.Figure(go.Bar(
                x=df_cis.iloc[:, 0],
                y=df_cis.iloc[:, 1].astype(float),
                marker_color=["#f85149" if float(v) > 28
                              else "#d29922" if float(v) > 18
                              else "#3fb950"
                              for v in df_cis.iloc[:, 1]],
                text=[f"{float(v):.1f}%" for v in df_cis.iloc[:, 1]],
                textposition="outside",
            ))
            fig_cis.update_layout(**PLOT, height=320,
                                   title="% que lo señala entre sus problemas (CIS 2025)",
                                   xaxis=dict(tickangle=-30, gridcolor="#21262d"),
                                   yaxis=dict(gridcolor="#21262d", range=[0, 45]))
            st.plotly_chart(fig_cis, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Evolución IPC vs Salarios — Pérdida de poder adquisitivo")
    años_ipc = [2020, 2021, 2022, 2023, 2024, 2025]
    ipc_ac   = [0.0,  3.1,  8.4,  13.2, 16.1, 18.4]
    sal_ac   = [0.0,  1.2,  3.1,   5.8,  7.9,  9.2]

    fig_ipc = go.Figure()
    fig_ipc.add_trace(go.Scatter(
        x=años_ipc, y=ipc_ac, name="IPC acumulado",
        mode="lines+markers",
        line=dict(color="#f85149", width=2),
        fill="tozeroy", fillcolor="rgba(248,81,73,0.1)",
    ))
    fig_ipc.add_trace(go.Scatter(
        x=años_ipc, y=sal_ac, name="Salarios acumulado",
        mode="lines+markers",
        line=dict(color="#3fb950", width=2),
        fill="tozeroy", fillcolor="rgba(63,185,80,0.1)",
    ))
    fig_ipc.update_layout(**PLOT, height=280,
                           title="IPC vs Salarios — Brecha acumulada 2020-2025 (%)",
                           yaxis=dict(gridcolor="#21262d", title="%"),
                           legend=dict(bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_ipc, use_container_width=True)

    st.error("⚠️ **Brecha de poder adquisitivo:** El IPC acumulado (+18.4%) dobla el "
             "crecimiento salarial acumulado (+9.2%) en el período 2020-2025. "
             "Los hogares con renta baja han perdido entre 2.800€ y 4.200€ anuales "
             "de poder adquisitivo real. (INE / Banco de España 2025)")



# ══════════════════════════════════════════════════════════════
# TAB 9 — MAPAS CCAA
# ══════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════
# TAB 10 — MAPAS CCAA  (reemplazar el bloque with tabs[9] existente)
# ══════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown("#### 🗺️ Indicadores por Comunidad Autónoma")
    fuentes("INE/EPA", "Idealista/BdE", "SNS-Ministerio Sanidad", "INE ECV")

    # ── Selector de indicador ────────────────────────────────
    INDICADORES = {
        "💼 Paro general":        "paro",
        "👶 Paro juvenil (<25)":  "paro_juvenil",
        "🏠 Precio vivienda €/m²":"vivienda",
        "🏥 Espera quirúrgica":   "sanidad",
        "💰 Renta media hogar":   "renta",
    }
    indicador_label = st.selectbox(
        "Selecciona indicador:",
        list(INDICADORES.keys()),
        index=0,
    )
    indicador_key = INDICADORES[indicador_label]

    col_mapa, col_rank = st.columns([3, 1])

    # ── Datos y figura según indicador ──────────────────────
    with col_mapa:
        if indicador_key == "paro":
            df_ccaa = query(
                "SELECT ccaa, tasa_paro FROM paro_ccaa_real ORDER BY tasa_paro DESC"
            )
            if df_ccaa.empty:
                # fallback datos embebidos
                df_ccaa = pd.DataFrame({
                    "ccaa": [
                        "Ceuta","Melilla","Canarias","Andalucía","Extremadura",
                        "Murcia","C. Valenciana","Castilla-La Mancha","Galicia",
                        "Asturias","Aragón","Cantabria","Baleares","Cataluña",
                        "La Rioja","Castilla y León","Madrid","Navarra","País Vasco",
                    ],
                    "tasa_paro": [
                        28.4,26.1,21.8,19.7,19.2,
                        16.8,15.4,14.2,12.8,
                        12.4,10.9,11.2,9.8,9.1,
                        8.7,10.2,9.8,8.2,8.1,
                    ],
                })
            if HAS_MAPA:
                fig_m = mc.mapa_paro_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("tasa_paro", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["tasa_paro"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if t>=15 else "#d29922" if t>=10 else "#3fb950"
                                  for t in df_s["tasa_paro"]],
                    text=[f"{v:.1f}%" for v in df_s["tasa_paro"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Tasa de paro EPA 2025T3",
                    xaxis=dict(gridcolor="#21262d", range=[0, 32]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("tasa_paro", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "tasa_paro", "%"
            rank_alerta = lambda v: "alerta" if v>=15 else "warning" if v>=10 else "ok"
            rank_icon   = lambda v: "🔴" if v>=15 else "🟡" if v>=10 else "🟢"

        elif indicador_key == "paro_juvenil":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Ceuta","Melilla","Andalucía","Extremadura","Canarias",
                    "Murcia","C. Valenciana","Castilla-La Mancha","Galicia",
                    "Asturias","Castilla y León","Aragón","Cantabria",
                    "Cataluña","Madrid","Baleares","La Rioja","Navarra","País Vasco",
                ],
                "paro_juvenil": [
                    55.1,51.3,42.1,40.8,38.4,
                    35.2,32.4,31.8,28.9,
                    27.4,22.6,22.1,24.8,
                    21.5,19.2,20.1,18.4,17.8,15.9,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_paro_juvenil_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("paro_juvenil", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["paro_juvenil"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if t>=35 else "#d29922" if t>=25 else "#3fb950"
                                  for t in df_s["paro_juvenil"]],
                    text=[f"{v:.1f}%" for v in df_s["paro_juvenil"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Paro juvenil <25 años EPA 2025 (%)",
                    xaxis=dict(gridcolor="#21262d", range=[0, 65]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("paro_juvenil", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "paro_juvenil", "%"
            rank_alerta = lambda v: "alerta" if v>=35 else "warning" if v>=25 else "ok"
            rank_icon   = lambda v: "🔴" if v>=35 else "🟡" if v>=25 else "🟢"

        elif indicador_key == "vivienda":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Madrid","Baleares","Cataluña","País Vasco","Canarias",
                    "Navarra","C. Valenciana","Andalucía","Cantabria",
                    "Aragón","Galicia","Asturias","La Rioja",
                    "Castilla y León","Murcia","Castilla-La Mancha","Extremadura",
                ],
                "precio_m2": [
                    4800,4200,3100,2850,2100,
                    1920,1820,1650,1580,
                    1420,1290,1180,1050,
                    1150,1240,980,860,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_vivienda_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("precio_m2", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["precio_m2"], y=df_s["ccaa"], orientation="h",
                    marker_color="#f0883e",
                    text=[f"{v:,.0f}€" for v in df_s["precio_m2"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Precio vivienda €/m² — Idealista/BdE 2025",
                    xaxis=dict(gridcolor="#21262d", range=[0, 5500]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("precio_m2", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "precio_m2", "€/m²"
            rank_alerta = lambda v: "alerta" if v>=3000 else "warning" if v>=2000 else "ok"
            rank_icon   = lambda v: "🔴" if v>=3000 else "🟡" if v>=2000 else "🟢"

        elif indicador_key == "sanidad":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Ceuta","Melilla","Canarias","Andalucía","C. Valenciana",
                    "Cataluña","Murcia","Extremadura","Galicia",
                    "Castilla-La Mancha","Castilla y León","Asturias",
                    "Aragón","Baleares","Cantabria","Madrid",
                    "Navarra","La Rioja","País Vasco",
                ],
                "dias_espera": [
                    201,188,168,156,142,
                    134,131,145,121,
                    122,118,115,
                    109,127,103,98,
                    92,88,87,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_sanidad_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("dias_espera", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["dias_espera"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if d>=150 else "#d29922" if d>=120 else "#3fb950"
                                  for d in df_s["dias_espera"]],
                    text=[f"{v}d" for v in df_s["dias_espera"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Días medios espera quirúrgica — SNS 2025",
                    xaxis=dict(gridcolor="#21262d", range=[0, 230]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("dias_espera", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "dias_espera", "d"
            rank_alerta = lambda v: "alerta" if v>=150 else "warning" if v>=120 else "ok"
            rank_icon   = lambda v: "🔴" if v>=150 else "🟡" if v>=120 else "🟢"

        else:  # renta
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Madrid","País Vasco","Navarra","Cataluña","Baleares",
                    "La Rioja","Cantabria","Aragón","Asturias","C. Valenciana",
                    "Castilla y León","Galicia","Murcia","Canarias",
                    "Castilla-La Mancha","Andalucía","Ceuta","Melilla","Extremadura",
                ],
                "renta_hogar": [
                    36200,35800,34100,30400,29800,
                    27900,27200,26800,25900,24700,
                    24200,23800,22100,22400,
                    21800,21200,21600,20800,19400,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_renta_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("renta_hogar", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["renta_hogar"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#3fb950" if v>=30000 else "#d29922" if v>=24000 else "#f85149"
                                  for v in df_s["renta_hogar"]],
                    text=[f"{v:,.0f}€" for v in df_s["renta_hogar"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Renta media por hogar — INE ECV 2025 (€/año)",
                    xaxis=dict(gridcolor="#21262d", range=[0, 40000]))
            st.plotly_chart(fig_m, use_container_width=True)
            # ranking invertido: más renta = mejor (verde)
            df_rank = df_ccaa.sort_values("renta_hogar", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "renta_hogar", "€"
            rank_alerta = lambda v: "ok" if v>=30000 else "warning" if v>=24000 else "alerta"
            rank_icon   = lambda v: "🟢" if v>=30000 else "🟡" if v>=24000 else "🔴"

    # ── Columna ranking ──────────────────────────────────────
    with col_rank:
        st.markdown("**Ranking**")
        for _, r in df_rank.iterrows():
            v   = r[rank_val]
            css = rank_alerta(v)
            ico = rank_icon(v)
            # formato valor
            if rank_unit in ("%",):
                val_fmt = f"{v:.1f}{rank_unit}"
            elif rank_unit in ("d",):
                val_fmt = f"{v:.0f} días"
            else:
                val_fmt = f"{v:,.0f} {rank_unit}"
            st.markdown(f"""
            <div class='kpi-card {css}'
                 style='padding:6px 10px;margin-bottom:3px'>
                <span style='font-size:0.78rem'>{ico} {r[rank_col]}</span><br>
                <b style='font-family:JetBrains Mono;font-size:0.82rem'>
                    {val_fmt}</b>
            </div>""", unsafe_allow_html=True)

    # ── Nota metodológica ────────────────────────────────────
    notas = {
        "paro":        "Tasa de paro EPA 2025T3. Fuente: INE. Media nacional: 11.4%",
        "paro_juvenil":"Paro <25 años. Fuente: EPA/INE 2025T3. Media UE: 14.9%",
        "vivienda":    "Precio medio venta €/m². Fuente: Idealista + Banco de España Q1 2026",
        "sanidad":     "Días medios espera quirúrgica. Fuente: SNS / Ministerio Sanidad 2025",
        "renta":       "Renta media neta por hogar. Fuente: INE Encuesta Condiciones de Vida 2025",
    }
    st.caption(f"📌 {notas[indicador_key]}")




with tabs[10]:
    st.markdown("#### 🔬 Metodología, fuentes y trazabilidad")

    st.markdown("""
    ## Sobre CitizenWatch Pro

    **CitizenWatch Pro** es una plataforma de inteligencia ciudadana independiente que 
    agrega, procesa y visualiza datos públicos oficiales sobre las principales 
    preocupaciones de la ciudadanía española.

    ### Fuentes de datos

    | Módulo | Fuente primaria | Actualización | URL |
    |--------|----------------|---------------|-----|
    | Barómetro social | CIS — Barómetro mensual | Mensual | datos.cis.es |
    | Empleo / Paro | INE — EPA | Trimestral | ine.es/dyngs/INEbase |
    | Vivienda | Banco de España + Idealista | Mensual | bde.es |
    | Seguridad | Ministerio del Interior | Anual | interior.gob.es |
    | Gasto político | Portal Transparencia + BOE | Continua | transparencia.gob.es |
    | Inmigración | INE Padrón + Eurostat | Trimestral | ine.es |
    | Sanidad | SNS — Ministerio Sanidad | Semestral | mscbs.gob.es |

    ### Pipeline de datos

    1. **Recolección:** Scripts Python ejecutados diariamente (cron 06:00 CET) 
       en Odroid C2 procesan APIs JSON del INE, Eurostat y datos.gob.es
    2. **Almacenamiento:** SQLite local en Odroid C2 — ligero, sin dependencias cloud
    3. **Normalización:** Limpieza de valores nulos, conversión de unidades, 
       deduplicación de registros
    4. **Visualización:** Streamlit + Plotly — actualización automática cada hora

    ### Limitaciones y avisos

    - Los datos de criminalidad son percepciones y estadísticas oficiales, 
      no reflejan la totalidad de delitos (cifra negra)
    - Los datos del CIS son encuestas de opinión, no hechos objetivos
    - Algunos datos tienen retardo de publicación de 3-6 meses

    ### Términos de uso

    Datos bajo licencia abierta CC-BY. Cita recomendada:
    *CitizenWatch Pro (2026). Plataforma de Auditoría Ciudadana España. 
    github.com/mcasrom*
    """)

    st.divider()
    st.markdown(f"""
    <div style='font-size:0.75rem;color:#8b949e;font-family:JetBrains Mono'>
    🖥️ Infraestructura: Odroid C2 · DietPi · Python 3.11 · Streamlit · SQLite<br>
    📦 Versión: 2.0.0 · Build: {datetime.now().strftime('%Y%m%d')}<br>
    🔒 Sin cookies · Sin tracking · Sin publicidad<br>
    © 2026 CitizenWatch Pro — Investigación independiente
    </div>
    """, unsafe_allow_html=True)
