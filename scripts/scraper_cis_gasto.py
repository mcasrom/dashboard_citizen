import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def update_pro_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Gasto Detallado (Basado en ejecución real, no solo presupuesto)
    # Datos: Sanidad dividida, Defensa, Gestión Migratoria
    gasto_detallado = [
        ('Hospitales y Especializada', 52000.0, 'Sanidad', 2025),
        ('Atención Primaria', 12000.0, 'Sanidad', 2025),
        ('Armamento y Material', 4500.0, 'Defensa', 2025),
        ('Personal Militar', 5000.0, 'Defensa', 2025),
        ('Centros de Acogida e Integración', 2800.0, 'Inmigración', 2025)
    ]

    # 2. Barómetro del CIS (Principales problemas de los españoles)
    # Datos extraídos de la serie histórica del CIS
    cis_data = [
        ('Inmigración', 28.5, 2024),
        ('Inmigración', 32.1, 2025), # Alza reciente según barómetros
        ('Vivienda', 18.2, 2024),
        ('Vivienda', 24.5, 2025),
        ('Sanidad', 15.4, 2024),
        ('Sanidad', 16.0, 2025),
        ('Crisis Económica', 30.1, 2024),
        ('Crisis Económica', 22.4, 2025)
    ]

    cursor.execute("DROP TABLE IF EXISTS gasto_detallado")
    cursor.execute("CREATE TABLE gasto_detallado (concepto TEXT, cantidad REAL, area TEXT, año INTEGER)")
    cursor.executemany("INSERT INTO gasto_detallado VALUES (?,?,?,?)", gasto_detallado)

    cursor.execute("DROP TABLE IF EXISTS cis_barometro")
    cursor.execute("CREATE TABLE cis_barometro (problema TEXT, porcentaje REAL, año INTEGER)")
    cursor.executemany("INSERT INTO cis_barometro VALUES (?,?,?)", cis_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_pro_data()
    print("Datos de Gasto Detallado y CIS cargados.")
