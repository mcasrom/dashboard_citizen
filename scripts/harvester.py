import pandas as pd
import requests
import os
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/dashboard_citizen/data")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def get_cesta_compra():
    try:
        url = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/50913?nult=24"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        records = []
        for serie in r.json():
            nombre = serie['Nombre']
            for h in serie['Data']:
                records.append({'Producto': nombre, 'Fecha': h['Fecha'], 'Valor': h['Valor']})
        pd.DataFrame(records).to_csv(f"{OUTPUT_DIR}/cesta_compra.csv", index=False)
        print("✅ INE: Sincronizado.")
    except Exception as e:
        print(f"⚠️ INE: No disponible actualmente.")

def get_combustibles():
    try:
        # Intentamos con un User-Agent para que el Ministerio no nos bloquee por parecer un bot
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = "https://geoportalgasolineras.minetur.gob.es/GVP/Servicios/ServicioRestPrecios.svc/PrecioCarburantes/Global"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        data = r.json()
        df = pd.DataFrame(data['ListaEESSPrecio'])
        for col in ['PrecioGasolina95E5', 'PrecioGasoilA']:
            df[col] = df[col].str.replace(',', '.').astype(float)
        
        new_row = pd.DataFrame([{
            'Fecha': datetime.now().strftime("%Y-%m-%d"),
            'G95': df['PrecioGasolina95E5'].mean(),
            'Diesel': df['PrecioGasoilA'].mean()
        }])
        
        hist_file = f"{OUTPUT_DIR}/combustibles_hist.csv"
        if os.path.exists(hist_file):
            df = pd.concat([pd.read_csv(hist_file), new_row]).drop_duplicates(subset='Fecha', keep='last')
        else:
            df = new_row
        df.to_csv(hist_file, index=False)
        print("✅ Combustibles: Actualizados.")
    except Exception:
        print("⚠️ Ministerio: Servidor fuera de línea o bloqueando peticiones.")

if __name__ == "__main__":
    get_cesta_compra()
    get_combustibles()
