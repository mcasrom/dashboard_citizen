import pandas as pd
import requests
import os

OUTPUT_DIR = os.path.expanduser("~/dashboard_citizen/data")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def get_cesta_compra():
    try:
        # Recuperamos los últimos 24 meses de la cesta de la compra
        url = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/50913?nult=24"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        records = []
        for serie in r.json():
            nombre = serie['Nombre']
            for h in serie['Data']:
                records.append({'Producto': nombre, 'Fecha': h['Fecha'], 'Valor': h['Valor']})
        
        df = pd.DataFrame(records)
        df.to_csv(f"{OUTPUT_DIR}/cesta_compra.csv", index=False)
        print(f"✅ INE: {len(df)} registros sincronizados correctamente.")
    except Exception as e:
        print(f"⚠️ Error al conectar con INE: {e}")

if __name__ == "__main__":
    get_cesta_compra()
