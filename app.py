import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

st.title("🏛️ Monitor de Supervivencia y Mercados")
st.caption(f"Nodo Soberano ODROID-C2 | Usuario: mcasrom")

tabs = st.tabs(["🛒 Cesta", "🏠 Vivienda", "📈 Finanzas", "⛽ Energía"])

# --- TAB 1: CESTA ---
with tabs[0]:
    df_cesta = load_data("/home/dietpi/dashboard_citizen/data/cesta_compra.csv")
    if not df_cesta.empty:
        df_clean = df_cesta[df_cesta['Concepto'].str.contains('Variación anual', case=False)].copy()
        df_clean['Concepto'] = df_clean['Concepto'].str.replace('Total Nacional. ', '', regex=False).str.strip()
        sel = st.multiselect("Categorías:", sorted(df_clean['Concepto'].unique()), default=[df_clean['Concepto'].iloc[0]])
        st.plotly_chart(px.line(df_clean[df_clean['Concepto'].isin(sel)], x='Fecha', y='Valor', color='Concepto', template="plotly_dark"), use_container_width=True)

# --- TAB 2: VIVIENDA (Filtro Relajado) ---
with tabs[1]:
    df_viv = load_data("/home/dietpi/dashboard_citizen/data/vivienda.csv")
    if not df_viv.empty:
        # Mostramos todo lo que venga en el archivo para asegurar que salga el gráfico
        fig_v = px.line(df_viv, x='Fecha', y='Valor', color='Concepto', markers=True, template="plotly_dark", title="Evolución Precios Vivienda")
        st.plotly_chart(fig_v, use_container_width=True)
    else:
        st.warning("No hay datos en vivienda.csv. Ejecuta el harvester.")

# --- TAB 3: FINANZAS ---
with tabs[2]:
    df_fin = load_data("/home/dietpi/dashboard_citizen/data/finanzas.csv")
    if not df_fin.empty:
        st.plotly_chart(px.line(df_fin, x='Fecha', y='Valor', color='Concepto', template="plotly_dark"), use_container_width=True)

# --- TAB 4: ENERGÍA (Simulación de estructura) ---
with tabs[3]:
    path_fuel = "/home/dietpi/dashboard_citizen/data/combustibles_hist.csv"
    if os.path.exists(path_fuel) and os.path.getsize(path_fuel) > 0:
        df_fuel = load_data(path_fuel)
        st.plotly_chart(px.line(df_fuel, x='Fecha', y=['G95', 'Diesel'], template="plotly_dark"), use_container_width=True)
    else:
        st.info("⛽ Los gráficos de Energía aparecerán automáticamente cuando el Ministerio abra el lunes.")
