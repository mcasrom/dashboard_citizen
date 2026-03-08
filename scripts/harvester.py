import pandas as pd
import requests
import os

OUTPUT_DIR = "data"
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def get_cesta_compra():
    try:
        # Tabla 50913: Índices de subclases
        url = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/50913?nult=12"
        r = requests.get(url, timeout=20).json()
        
        records = []
        for serie in r:
            nombre = serie['Nombre']
            # Guardamos TODO para ver qué hay dentro
            for h in serie['Data']:
                records.append({
                    'Producto': nombre,
                    'Fecha': h['Fecha'],
                    'Variacion_Anual': h['Valor']
                })
        
        df = pd.DataFrame(records)
        if not df.empty:
            df.to_csv(f"{OUTPUT_DIR}/cesta_compra.csv", index=False)
            print(f"✅ ÉXITO: {len(df)} registros guardados.")
            print("Muestra de productos capturados:", df['Producto'].unique()[:3])
        else:
            print("❌ La API devolvió una lista vacía.")
            
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    get_cesta_compra()
