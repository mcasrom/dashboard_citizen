import pandas as pd
import json

def analyze_mercosur_diff():
    # Datos de investigación OSINT sobre regulaciones
    # Basado en alertas de seguridad alimentaria (RASFF)
    comparativa = [
        {
            "producto": "Carne Bovina",
            "motivo_barato": "Uso de promotores de crecimiento prohibidos en EU",
            "norma_eu": "Reglamento (CE) 124/2009",
            "estatus": "Crítico"
        },
        {
            "producto": "Cereales / Soja",
            "motivo_barato": "Límites de fitosanitarios (Glifosato) más laxos",
            "norma_eu": "Directiva 91/414/CEE",
            "estatus": "Alerta"
        }
    ]
    
    with open('/home/dietpi/citizen-watch-osint/data/mercosur_alerts.json', 'w') as f:
        json.dump(comparativa, f, indent=4)

if __name__ == "__main__":
    analyze_mercosur_diff()
    print("Análisis Mercosur completado.")
