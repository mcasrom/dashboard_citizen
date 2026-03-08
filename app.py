import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Ciudadano Pro: Energía y Cesta", layout="wide")

# Carga de datos con gestión de errores
def load_data(name):
    path = os.path.expanduser(f"~/dashboard_citizen/data/{name}.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

df_cesta = load_data('cesta_compra.csv')
df_fuel = load_data('combustibles_hist.csv')

st.title("🏛️ Monitor de Supervivencia Ciudadana")
st.caption("Nodo Soberano ODROID-C2 | Datos en Tiempo Real")

# --- BLOQUE 1: CARBURANTES (PETRÓLEO/GASOLINA) ---
st.subheader("⛽ Energía y Combustibles")
if not df_fuel.empty:
    c1, c2, c3 = st.columns(3)
    latest = df_fuel.iloc[-1]
    c1.metric("Gasolina 95", f"{latest['G95']:.3f} €/L")
    c2.metric("Gasóleo A", f"{latest['Diesel']:.3f} €/L")
    c3.metric("Fecha Actualización", latest['Fecha'])
    
    fig_fuel = px.line(df_fuel, x='Fecha', y=['G95', 'Diesel'], 
                       title="Evolución Carburantes", template="plotly_dark",
                       color_discrete_sequence=['#FF4B4B', '#00CC96'])
    st.plotly_chart(fig_fuel, use_container_width=True)

# --- BLOQUE 2: ALIMENTOS ---
st.divider()
st.subheader("🛒 Cesta de la Compra")
if not df_cesta.empty:
    # Limpieza para el usuario
    df_cesta = df_cesta[df_cesta['Producto'].str.contains('Variación anual', case=False)]
    df_cesta['Producto'] = df_cesta['Producto'].str.replace('Total Nacional. ', '').str.replace('. Variación anual.', '')
    
    opciones = st.multiselect("Comparar alimentos:", sorted(df_cesta['Producto'].unique()), default=["Alimentos y bebidas no alcohólicas", "Aceites y grasas"])
    df_filt = df_cesta[df_cesta['Producto'].isin(opciones)]
    
    fig_cesta = px.line(df_filt, x='Fecha', y='Valor', color='Producto', 
                        markers=True, template="plotly_dark")
    st.plotly_chart(fig_cesta, use_container_width=True)

# --- ROTACIÓN Y MANTENIMIENTO ---
st.sidebar.write("⚙️ **Mantenimiento ODROID**")
st.sidebar.info(f"Registros en Cesta: {len(df_cesta)}")
st.sidebar.info(f"Registros en Combustibles: {len(df_fuel)}")
