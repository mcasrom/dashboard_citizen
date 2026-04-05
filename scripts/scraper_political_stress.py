import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def update_political_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. ÍNDICE DE CORRUPCIÓN Y POLÍTICA (CIS SEGMENTADO)
    # Refleja la percepción de la política como "Problema Principal"
    political_stress = [
        ('Corrupción y Fraude', 18.5, 'Percepción Ética'),
        ('El mal comportamiento de los políticos', 34.2, 'Desafección'),
        ('Los problemas de índole política', 22.8, 'Inoperancia'),
        ('La falta de acuerdos / Bloqueo', 15.4, 'Inestabilidad')
    ]

    # 2. GASTO EN ESTRUCTURA POLÍTICA vs SERVICIOS (Simulado OSINT)
    # Comparativa de "Músculo Político" vs "Músculo Social"
    gasto_comparativo = [
        ('Asesores y Cargos a Dedo', 1200, 'Estructura Política'),
        ('Publicidad Institucional', 850, 'Estructura Política'),
        ('Investigación Universitaria', 600, 'Servicio Público'),
        ('Salud Mental (Presupuesto)', 400, 'Servicio Público')
    ]

    cursor.execute("DROP TABLE IF EXISTS political_perception")
    cursor.execute("CREATE TABLE political_perception (indicador TEXT, porcentaje REAL, categoria TEXT)")
    cursor.executemany("INSERT INTO political_perception VALUES (?,?,?)", political_stress)

    cursor.execute("DROP TABLE IF EXISTS gasto_politico_vs_social")
    cursor.execute("CREATE TABLE gasto_politico_vs_social (concepto TEXT, cantidad REAL, tipo TEXT)")
    cursor.executemany("INSERT INTO gasto_politico_vs_social VALUES (?,?,?)", gasto_comparativo)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_political_data()
    print("Índice de Tensión Política cargado en la ODROID-C2.")
