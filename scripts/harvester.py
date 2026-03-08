import pandas as pd
import requests
import os

OUTPUT_DIR = os.path.expanduser("~/dashboard_citizen/data")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def get_ine_data(id_tabla, nombre_archivo, ultimos=12):
    try:
        # Intentamos la conexión
        url = f"https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/{id_tabla}?nult={ultimos}"
        r = requests.get(url, timeout=20)
        
        if r.status_code == 200:
            records = []
            for serie in r.json():
                nombre = serie['Nombre']
                for h in serie['Data']:
                    records.append({'Concepto': nombre, 'Fecha': h['Fecha'], 'Valor': h['Valor']})
            if records:
                pd.DataFrame(records).to_csv(f"{OUTPUT_DIR}/{nombre_archivo}.csv", index=False)
                print(f"✅ {nombre_archivo} sincronizado.")
                return True
        print(f"⚠️ Tabla {id_tabla} no disponible (Status {r.status_code}).")
        return False
    except Exception as e:
        print(f"❌ Error en {nombre_archivo}: {e}")
        return False

if __name__ == "__main__":
    # 1. Cesta de la Compra (ID Robusto)
    get_ine_data("50913", "cesta_compra", ultimos=24)
    
    # 2. Vivienda (IPV)
    get_ine_data("25171", "vivienda", ultimos=12)
    
    # 3. Finanzas (Intentamos Euríbor, si falla, traemos el IPC General como referencia)
    if not get_ine_data("3616", "finanzas", ultimos=12):
        print("🔄 Aplicando plan B: Capturando IPC General para Finanzas...")
        get_ine_data("50902", "finanzas", ultimos=12)
