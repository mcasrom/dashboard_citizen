import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def update_ultra_pro_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. AMPLIACIÓN CIS: Las 10 Inquietudes Reales (Segmentadas)
    cis_full = [
        ('Inmigración (Gestión y Flujos)', 34.2, 2025, 'Alta'),
        ('Vivienda (Precio y Desahucios)', 28.1, 2025, 'Crítica'),
        ('Paro y Precariedad Laboral', 25.5, 2025, 'Estructural'),
        ('Sanidad (Listas de Espera)', 18.3, 2025, 'Alta'),
        ('Problemas Económicos / IPC', 31.8, 2025, 'Crítica'),
        ('Inseguridad Ciudadana', 12.4, 2025, 'Creciente'),
        ('Educación / Universidad', 8.2, 2025, 'Media'),
        ('Corrupción y Fraude', 14.7, 2025, 'Persistente'),
        ('Precios de la Energía', 22.9, 2025, 'Alta'),
        ('Calidad de los Alimentos (Tratados)', 9.5, 2025, 'Emergente')
    ]

    # 2. VECTOR MERCOSUR: Por qué es una amenaza ciudadana (OSINT)
    mercosur_risks = [
        ('Carne Bovina', 'Dumping', 'Uso de Hormonas Estrógenos prohibidas en EU', 'Impacto Salud'),
        ('Cereales', 'IPC', 'Pesticidas Neonicotinoides prohibidos', 'Impacto Ambiental'),
        ('Pollo', 'Seguridad', 'Lavado con Cloro (Standard no EU)', 'Riesgo Alergenos')
    ]

    # 3. GASTO DETALLADO (Split Real 2025)
    gasto_pro = [
        ('Hospitales/Urgencias', 45000, 'Sanidad'),
        ('Atención Primaria', 11000, 'Sanidad'),
        ('Becas Universitarias', 2100, 'Educación'),
        ('Seguridad (Cuerpos Policiales)', 9800, 'Defensa/Seguro'),
        ('Subsidios Energía', 4500, 'Economía'),
        ('Control Fronterizo', 3200, 'Inmigración')
    ]

    cursor.execute("DROP TABLE IF EXISTS cis_full")
    cursor.execute("CREATE TABLE cis_full (problema TEXT, porcentaje REAL, año INTEGER, nivel TEXT)")
    cursor.executemany("INSERT INTO cis_full VALUES (?,?,?,?)", cis_full)

    cursor.execute("DROP TABLE IF EXISTS mercosur_impact")
    cursor.execute("CREATE TABLE mercosur_impact (producto TEXT, tipo TEXT, riesgo TEXT, area TEXT)")
    cursor.executemany("INSERT INTO mercosur_impact VALUES (?,?,?,?)", mercosur_risks)

    cursor.execute("DROP TABLE IF EXISTS gasto_detallado_pro")
    cursor.execute("CREATE TABLE gasto_detallado_pro (concepto TEXT, cantidad REAL, area TEXT)")
    cursor.executemany("INSERT INTO gasto_detallado_pro VALUES (?,?,?)", gasto_pro)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_ultra_pro_data()
    print("Músculo de datos Citizen-Watch actualizado al 100%.")
