import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Ciudadano Pro: Inteligencia Económica", layout="wide")

DATA_PATH = "/home/dietpi/dashboard_citizen/data/cesta_compra.csv"

st.title("🏛️ Monitor de Supervivencia Ciudadana")
st.caption("Nodo Soberano ODROID-C2 | Análisis de Inflación Real")

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    
    # 1. Limpieza y preparación
    df_clean = df[df['Producto'].str.contains('Variación anual', case=False, na=False)].copy()
    df_clean['Producto'] = df_clean['Producto'].str.replace('Total Nacional. ', '', regex=False).str.replace('. Variación anual.', '', regex=False).str.strip()
    df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha'])
    
    # Obtener lista única de opciones
    opciones = sorted(df_clean['Producto'].unique().tolist())
    
    # BUSCADOR DINÁMICO DE DEFAULT:
    # Buscamos qué opciones contienen "Alimentos" o "Aceites" para que no de error
    defaults_encontrados = [opt for opt in opciones if "Alimentos" in opt or "Aceites" in opt]
    # Si no encuentra nada, coge la primera opción disponible para evitar el crash
    final_default = [defaults_encontrados[0]] if defaults_encontrados else [opciones[0]]

    # 2. Métricas
    c1, c2, c3 = st.columns(3)
    # Intentamos sacar el dato de Alimentos si existe
    df_alimentos = df_clean[df_clean['Producto'].str.contains('Alimentos', case=False)]
    if not df_alimentos.empty:
        reciente = df_alimentos.sort_values('Fecha').iloc[-1]
        c1.metric("Inflación Alimentos", f"{reciente['Valor']}%", delta_color="inverse")
        c3.metric("Última Actualización", reciente['Fecha'].strftime('%m/%Y'))
    
    c2.metric("Registros en Memoria", f"{len(df):,}")

    # 3. Multiselect Seguro
    seleccion = st.multiselect("Selecciona productos para comparar:", 
                               opciones, 
                               default=final_default)
    
    if seleccion:
        fig = px.line(df_clean[df_clean['Producto'].isin(seleccion)], 
                      x='Fecha', y='Valor', color='Producto',
                      markers=True, template="plotly_dark", title="Evolución Histórica (%)")
        st.plotly_chart(fig, use_container_width=True)

    # 4. Tabla
    st.subheader("🔥 Top 10 Subidas del Mes")
    ultima_fecha = df_clean['Fecha'].max()
    df_top = df_clean[df_clean['Fecha'] == ultima_fecha].sort_values('Valor', ascending=False).head(10)
    st.table(df_top[['Producto', 'Valor']])

else:
    st.error(f"No se encuentra el archivo en {DATA_PATH}")

st.sidebar.write("⚙️ **Nodo ODROID-C2**")
st.sidebar.info(f"Tamaño archivo: 2.0 MB")
