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
        # El INE usa milisegundos, si detectamos números grandes convertimos con unit='ms'
        if df['Fecha'].dtype != 'object':
            df['Fecha'] = pd.to_datetime(df['Fecha'], unit='ms')
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
    except:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    return df.dropna(subset=['Fecha'])

st.title("🏛️ Monitor de Supervivencia y Mercados")
st.caption(f"Nodo Soberano ODROID-C2 | Usuario: mcasrom")

tabs = st.tabs(["🛒 Cesta de la Compra", "🏠 Vivienda", "📈 Finanzas", "⛽ Energía"])

# --- TAB 1: CESTA DE LA COMPRA ---
with tabs[0]:
    df_cesta = load_data("/home/dietpi/dashboard_citizen/data/cesta_compra.csv")
    if not df_cesta.empty:
        df_clean = df_cesta[df_cesta['Concepto'].str.contains('Variación anual', case=False)].copy()
        df_clean['Concepto'] = df_clean['Concepto'].str.replace('Total Nacional. ', '', regex=False).str.replace('. Variación anual.', '', regex=False).str.strip()
        
        c1, c2 = st.columns(2)
        df_alim = df_clean[df_clean['Concepto'].str.contains('Alimentos', case=False)]
        if not df_alim.empty:
            reciente = df_alim.sort_values('Fecha').iloc[-1]
            c1.metric("Inflación Alimentos", f"{reciente['Valor']}%", delta_color="inverse")
            c2.metric("Actualización Cesta", reciente['Fecha'].strftime('%m/%Y'))

        opciones = sorted(df_clean['Concepto'].unique().tolist())
        defaults = [opt for opt in opciones if "Alimentos" in opt or "Aceites" in opt][:2]
        seleccion = st.multiselect("Comparar categorías:", opciones, default=defaults if defaults else opciones[:1])
        
        if seleccion:
            fig_cesta = px.line(df_clean[df_clean['Concepto'].isin(seleccion)].sort_values('Fecha'), 
                                x='Fecha', y='Valor', color='Concepto', markers=True, 
                                template="plotly_dark", title="Variación Anual IPC")
            st.plotly_chart(fig_cesta, use_container_width=True)
    else:
        st.info("Esperando datos de la cesta...")

# --- TAB 2: VIVIENDA ---
with tabs[1]:
    st.subheader("🏠 Mercado Inmobiliario")
    df_viv = load_data("/home/dietpi/dashboard_citizen/data/vivienda.csv")
    if not df_viv.empty:
        df_v_filt = df_viv[df_viv['Concepto'].str.contains('General', case=False)]
        fig_v = px.bar(df_v_filt, x='Fecha', y='Valor', color='Valor', 
                         color_continuous_scale='Reds', template="plotly_dark", title="Índice de Precios de Vivienda (IPV)")
        st.plotly_chart(fig_v, use_container_width=True)
    else:
        st.info("Datos de vivienda no disponibles.")

# --- TAB 3: FINANZAS (Euríbor) ---
with tabs[2]:
    st.subheader("📈 Tipos de Interés y Euríbor")
    df_fin = load_data("/home/dietpi/dashboard_citizen/data/finanzas.csv")
    if not df_fin.empty:
        # Filtramos para mostrar el Euríbor a un año
        df_eur = df_fin[df_fin['Concepto'].str.contains('Euríbor', case=False)]
        if not df_eur.empty:
            ultimo_e = df_eur.sort_values('Fecha').iloc[-1]
            st.metric("Euríbor a 1 año", f"{ultimo_e['Valor']}%")
            
            fig_f = px.line(df_eur, x='Fecha', y='Valor', color='Concepto', 
                            markers=True, template="plotly_dark", title="Evolución del Euríbor")
            st.plotly_chart(fig_f, use_container_width=True)
        else:
            st.write("Datos disponibles:", df_fin['Concepto'].unique())
    else:
        st.info("Sincronizando con indicadores financieros...")

# --- TAB 4: ENERGÍA ---
with tabs[3]:
    st.subheader("⛽ Combustibles")
    path_fuel = "/home/dietpi/dashboard_citizen/data/combustibles_hist.csv"
    if os.path.exists(path_fuel):
        df_fuel = load_data(path_fuel)
        if not df_fuel.empty:
            latest = df_fuel.sort_values('Fecha').iloc[-1]
            c1, c2 = st.columns(2)
            c1.metric("Gasolina 95", f"{latest['G95']:.3f} €/L")
            c2.metric("Gasóleo A", f"{latest['Diesel']:.3f} €/L")
            st.plotly_chart(px.line(df_fuel, x='Fecha', y=['G95', 'Diesel'], template="plotly_dark"), use_container_width=True)
        else:
            st.info("Archivo de energía vacío.")
    else:
        st.info("⛽ Módulo de energía: Esperando respuesta del Ministerio (Lunes apertura).")

st.sidebar.write("⚙️ **Mantenimiento Nodo**")
st.sidebar.info(f"Usuario: mcasrom")
