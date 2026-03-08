import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ciudadano Data: Cesta", layout="wide")

st.title("🛒 Monitor de la Cesta de la Compra")
st.caption("Datos oficiales analizados desde tu ODROID-C2")

try:
    df = pd.read_csv('data/cesta_compra.csv')
    
    # 1. FILTRADO: Solo nos interesan las "Variaciones anuales" para ver cuánto ha subido respecto al año pasado
    df = df[df['Producto'].str.contains('Variación anual', case=False, na=False)]
    
    # 2. LIMPIEZA: Acortamos los nombres para que queden estéticos
    # Pasamos de "Total Nacional. Alimentos. Variación anual." a "Alimentos"
    df['Producto'] = df['Producto'].str.replace('Total Nacional. ', '', regex=False)
    df['Producto'] = df['Producto'].str.replace('. Variación anual.', '', regex=False)
    
    # 3. INTERFAZ
    opciones = sorted(df['Producto'].unique())
    
    # Buscamos algunos por defecto para que no salga vacío
    defaults = [opt for opt in opciones if "Alimentos" in opt or "Aceites" in opt]
    
    seleccion = st.multiselect("🔍 Busca productos (ej: Alimentos, Pan, Cereales, Frutas):", 
                               opciones, 
                               default=defaults[:2] if defaults else opciones[:1])

    if seleccion:
        df_filt = df[df['Producto'].isin(seleccion)].copy()
        df_filt['Fecha'] = pd.to_datetime(df_filt['Fecha'])
        df_filt = df_filt.sort_values('Fecha')
        
        # Gráfico interactivo
        fig = px.line(df_filt, x='Fecha', y='Variacion_Anual', color='Producto', 
                      markers=True, template="plotly_dark",
                      labels={'Variacion_Anual': 'Subida Anual (%)', 'Fecha': 'Mes'})
        
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
        # Ranking de impacto
        st.subheader("🔥 Ranking de subidas actuales")
        ultimo_mes = df_filt['Fecha'].max()
        df_rank = df[df['Fecha'] == df['Fecha'].max()].sort_values('Variacion_Anual', ascending=False)
        
        # Filtramos para no mostrar el índice general en el ranking y ver solo alimentos
        st.table(df_rank[['Producto', 'Variacion_Anual']].head(10))
    else:
        st.info("Utiliza el buscador de arriba para añadir productos a la comparativa.")

except Exception as e:
    st.error(f"Error procesando datos: {e}")
    st.info("Prueba a ejecutar el harvester de nuevo si el error persiste.")
