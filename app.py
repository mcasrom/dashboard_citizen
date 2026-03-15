import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime

st.set_page_config(page_title="M. Castillo: Inteligencia Económica", layout="wide")

def load_data(path):
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty: return df
    try:
        if df['Fecha'].dtype != 'object':
            df['Fecha'] = pd.to_datetime(df['Fecha'], unit='ms')
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
    except:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    return df.dropna(subset=['Fecha'])

# ===============================
# ENERGÍA — FUNCIONES
# ===============================

@st.cache_data(ttl=3600)
def obtener_precios_carburantes():
    """Precios medios nacionales desde API MINETUR — 12.000+ estaciones."""
    URL = ("https://sedeaplicaciones.minetur.gob.es/"
           "ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/")
    try:
        r = requests.get(URL, timeout=20,
                         headers={"User-Agent": "dashboard-citizen/1.0",
                                  "Accept": "application/json"})
        if r.status_code != 200:
            return None
        data  = r.json()
        eess  = data.get("ListaEESSPrecio", [])
        fecha = data.get("Fecha", "")[:10]
        # DD/MM/YYYY → YYYY-MM-DD
        partes = fecha.replace("/", "-").split("-")
        if len(partes) == 3 and len(partes[2]) == 4:
            fecha = f"{partes[2]}-{partes[1]}-{partes[0]}"

        precios_95, precios_goa, precios_sp98 = [], [], []
        for e in eess:
            def parse(campo):
                v = e.get(campo, "").strip().replace(",", ".")
                try: return float(v)
                except: return None
            v95  = parse("Precio Gasolina 95 E5")
            vgoa = parse("Precio Gasoleo A")
            v98  = parse("Precio Gasolina 98 E5")
            if v95:  precios_95.append(v95)
            if vgoa: precios_goa.append(vgoa)
            if v98:  precios_sp98.append(v98)

        if not precios_95: return None
        return {
            "fecha":        fecha,
            "gasolina_95":  round(sum(precios_95)  / len(precios_95),  3),
            "gasoleo_a":    round(sum(precios_goa)  / len(precios_goa), 3) if precios_goa else None,
            "gasolina_98":  round(sum(precios_sp98) / len(precios_sp98),3) if precios_sp98 else None,
            "n_estaciones": len(eess),
        }
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def obtener_brent():
    """Precio Brent en USD desde datahub.io (sin API key)."""
    try:
        r = requests.get(
            "https://pkgstore.datahub.io/core/oil-prices/brent-daily_json/data/brent-daily_json.json",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if data:
                ultimo = data[-1]
                return {
                    "precio_usd": float(ultimo.get("Price", 0)),
                    "fecha":      ultimo.get("Date", "")[:10]
                }
    except:
        pass
    return None

# Referencia media UE (Oil Bulletin — actualización manual semanal)
UE_REF = {"gasolina_95": 1.594, "gasoleo_a": 1.526, "semana": "03/03/2026"}

# --- LÓGICA DE ALERTAS (Antes del UI) ---
df_c = load_data("/home/dietpi/dashboard_citizen/data/cesta_compra.csv")
alertas = []
if not df_c.empty:
    ultima_fecha = df_c['Fecha'].max()
    df_alertas = df_c[(df_c['Fecha'] == ultima_fecha) & (df_c['Valor'] >= 10.0)]
    for _, row in df_alertas.iterrows():
        nombre = row['Concepto'].replace('Total Nacional. ', '').replace('. Variación anual.', '').strip()
        alertas.append(f"🚨 **{nombre}**: +{row['Valor']}%")

# Alerta energía
precios_en = obtener_precios_carburantes()
if precios_en and precios_en["gasolina_95"] >= 1.65:
    alertas.append(f"⛽ **Gasolina 95**: {precios_en['gasolina_95']:.3f}€/L — por encima del umbral")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3859/3859124.png", width=100)
    st.title("Soberanía mcasrom")
    st.divider()
    st.subheader("⚠️ Alertas Críticas (>10%)")
    if alertas:
        for a in alertas:
            st.warning(a)
    else:
        st.success("✅ No hay anomalías graves este mes.")
    st.divider()
    st.info(f"Nodo: ODROID-C2\n\nAutor: M. Castillo")

# --- CUERPO PRINCIPAL ---
st.title("🏛️ Monitor de Supervivencia y Mercados")

tabs = st.tabs(["🛒 Cesta", "🏠 Vivienda", "📈 Finanzas", "⛽ Energía", "🔍 Comparativa"])

# --- TAB 1: CESTA ---
with tabs[0]:
    if not df_c.empty:
        df_c['Concepto'] = df_c['Concepto'].str.replace('Total Nacional. ', '', regex=False).str.strip()
        opciones = sorted([opt for opt in df_c['Concepto'].unique() if any(x in opt.lower() for x in ['alimento', 'bebida', 'aceite', 'carne', 'pescado', 'pan', 'fruta', 'legumbre'])])
        sel = st.multiselect("Filtro Alimentos:", opciones, default=[opciones[0]] if opciones else None)
        if sel:
            st.plotly_chart(px.line(df_c[df_c['Concepto'].isin(sel)], x='Fecha', y='Valor', color='Concepto', template="plotly_dark"), width='stretch')

# --- TAB 2: VIVIENDA ---
with tabs[1]:
    df_v = load_data("/home/dietpi/dashboard_citizen/data/vivienda.csv")
    if not df_v.empty:
        opciones_v = sorted([opt for opt in df_v['Concepto'].unique() if 'vivienda' in opt.lower()])
        sel_v = st.multiselect("Indicadores Vivienda:", opciones_v, default=[opciones_v[0]] if opciones_v else None)
        if sel_v:
            st.plotly_chart(px.line(df_v[df_v['Concepto'].isin(sel_v)], x='Fecha', y='Valor', color='Concepto', markers=True, template="plotly_dark"), width='stretch')

# --- TAB 3: FINANZAS ---
with tabs[2]:
    df_f = load_data("/home/dietpi/dashboard_citizen/data/finanzas.csv")
    if not df_f.empty:
        terminos_macro = ['índice general', 'ipc', 'euríbor', 'interés', 'inflación', 'subyacente']
        opciones_f = sorted([opt for opt in df_f['Concepto'].unique() if any(t in opt.lower() for t in terminos_macro)])
        sel_f = st.multiselect("Indicadores Macro:", opciones_f, default=[opciones_f[0]] if opciones_f else None)
        if sel_f:
            st.plotly_chart(px.line(df_f[df_f['Concepto'].isin(sel_f)], x='Fecha', y='Valor', color='Concepto', template="plotly_dark"), width='stretch')

# --- TAB 4: ENERGÍA ---
with tabs[3]:
    st.subheader("⛽ Precios de Combustibles — Datos en Tiempo Real")

    if precios_en:
        g95  = precios_en["gasolina_95"]
        goa  = precios_en["gasoleo_a"]
        g98  = precios_en["gasolina_98"]
        nest = precios_en["n_estaciones"]
        fech = precios_en["fecha"]
    else:
        g95, goa, g98, nest, fech = 1.549, 1.468, 1.689, 0, "No disponible"
        st.warning("⚠️ API MINETUR no disponible — mostrando último valor conocido")

    brent = obtener_brent()
    brent_usd = brent["precio_usd"] if brent else 71.5
    brent_eur = round(brent_usd * 0.92, 2)
    brent_fecha = brent["fecha"] if brent else "N/D"

    st.caption(f"📅 Actualizado: {fech}  |  🏪 {nest:,} estaciones  |  Brent: {brent_fecha}")

    # ---- KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⛽ Gasolina 95",   f"{g95:.3f} €/L",
                f"{g95 - UE_REF['gasolina_95']:+.3f} vs UE",
                delta_color="inverse")
    col2.metric("🚛 Gasóleo A",     f"{goa:.3f} €/L" if goa else "N/D",
                f"{goa - UE_REF['gasoleo_a']:+.3f} vs UE" if goa else "",
                delta_color="inverse")
    col3.metric("🛢️ Brent",        f"{brent_usd:.1f} $/b",
                f"{brent_eur:.1f} €/b")
    col4.metric("🔝 Gasolina 98",   f"{g98:.3f} €/L" if g98 else "N/D")

    st.markdown("---")

    # ---- COMPARATIVA ESPAÑA vs UE
    col_a, col_b = st.columns(2)
    with col_a:
        df_comp = pd.DataFrame({
            "Carburante": ["Gasolina 95", "Gasóleo A"],
            "España":     [g95, goa if goa else 0],
            "Media UE":   [UE_REF["gasolina_95"], UE_REF["gasoleo_a"]]
        }).melt(id_vars="Carburante", var_name="Región", value_name="€/L")
        fig_comp = px.bar(df_comp, x="Carburante", y="€/L",
                          color="Región",
                          color_discrete_map={"España": "#3498db", "Media UE": "#e67e22"},
                          barmode="group", text="€/L",
                          title="España vs Media UE (€/litro con impuestos)",
                          template="plotly_dark")
        fig_comp.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(fig_comp, width='stretch')

    with col_b:
        # Semáforo
        st.markdown("### 🚦 Semáforo de Presión al Bolsillo")
        def semaforo_citizen(precio, umbral_alto, umbral_critico, nombre, emoji):
            if precio is None:
                st.info(f"{emoji} **{nombre}**: Sin datos")
            elif precio >= umbral_critico:
                st.error(f"🔴 **{nombre}: {precio:.3f} €/L** — Precio CRÍTICO para el bolsillo")
            elif precio >= umbral_alto:
                st.warning(f"🟡 **{nombre}: {precio:.3f} €/L** — Precio ELEVADO")
            else:
                st.success(f"🟢 **{nombre}: {precio:.3f} €/L** — Precio asumible")

        semaforo_citizen(g95,  1.60, 1.75, "Gasolina 95", "⛽")
        semaforo_citizen(goa,  1.50, 1.65, "Gasóleo A",   "🚛")
        semaforo_citizen(g98,  1.70, 1.85, "Gasolina 98", "🔝")

        st.markdown("---")
        ahorro_mensual = None
        if goa and g95:
            litros_mes = st.slider("🚗 Litros/mes estimados", 20, 200, 60)
            ahorro = round((g95 - goa) * litros_mes, 2)
            st.metric("💰 Ahorro mensual diesel vs gasolina",
                      f"{ahorro:.2f} €/mes",
                      help=f"Si llenas {litros_mes}L de gasóleo en vez de gasolina 95")

    st.markdown("---")

    # ---- EVOLUCIÓN HISTÓRICA (desde CSV si existe, si no base hardcoded)
    st.subheader("📈 Evolución Histórica de Precios")
    hist_path = "/home/dietpi/dashboard_citizen/data/energia.csv"
    if os.path.exists(hist_path):
        df_ene = pd.read_csv(hist_path, parse_dates=["fecha"])
    else:
        # Base histórica hasta hoy
        df_ene = pd.DataFrame([
            {"fecha": "2025-01", "gasolina_95": 1.530, "gasoleo_a": 1.480, "brent_usd": 78.0},
            {"fecha": "2025-04", "gasolina_95": 1.498, "gasoleo_a": 1.442, "brent_usd": 73.5},
            {"fecha": "2025-07", "gasolina_95": 1.538, "gasoleo_a": 1.478, "brent_usd": 79.5},
            {"fecha": "2025-10", "gasolina_95": 1.502, "gasoleo_a": 1.445, "brent_usd": 74.5},
            {"fecha": "2026-01", "gasolina_95": 1.455, "gasoleo_a": 1.405, "brent_usd": 68.5},
            {"fecha": str(datetime.today())[:7], "gasolina_95": g95,
             "gasoleo_a": goa if goa else 1.468, "brent_usd": brent_usd},
        ])
        df_ene["fecha"] = pd.to_datetime(df_ene["fecha"])

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(x=df_ene["fecha"], y=df_ene["gasolina_95"],
                                   name="Gasolina 95", mode="lines+markers",
                                   line=dict(color="#e74c3c", width=3)))
    if "gasoleo_a" in df_ene.columns:
        fig_hist.add_trace(go.Scatter(x=df_ene["fecha"], y=df_ene["gasoleo_a"],
                                       name="Gasóleo A", mode="lines+markers",
                                       line=dict(color="#3498db", width=3)))
    fig_hist.add_hline(y=1.65, line_dash="dot", line_color="orange",
                       annotation_text="Umbral tensión 1.65€")
    fig_hist.update_layout(height=400, template="plotly_dark",
                           hovermode="x unified",
                           title="Evolución mensual €/litro",
                           yaxis_title="€/litro")
    st.plotly_chart(fig_hist, width='stretch')

# --- TAB 5: COMPARATIVA ---
with tabs[4]:
    st.subheader("🧪 Análisis Cruzado")
    df_all = pd.concat([df_c, df_v, df_f], ignore_index=True)
    if not df_all.empty:
        comparar = st.multiselect("Cruza cualquier dato:", sorted(df_all['Concepto'].unique()),
                                   default=[alertas[0].split('**')[1] if alertas else df_all['Concepto'].iloc[0]])
        st.plotly_chart(px.line(df_all[df_all['Concepto'].isin(comparar)],
                                x='Fecha', y='Valor', color='Concepto',
                                template="plotly_dark"), width='stretch')
