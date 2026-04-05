import sqlite3
import pandas as pd
import requests
import json
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gasto_publico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector TEXT,
            cantidad REAL,
            fecha DATE,
            fuente TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iniciativas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            categoria TEXT,
            votos INTEGER,
            estado TEXT,
            fecha_registro DATE
        )
    ''')
    conn.commit()
    conn.close()

def fetch_osint_data():
    # En un entorno real, aquí usaríamos requests.get() a APIs de datos.gob.es o similares
    # Simulamos la captura de datos críticos para el "Músculo" de la ODROID
    data_gasto = [
        ('Sanidad', 75400.50, datetime.now().strftime('%Y-%m-%d'), 'Portal Transparencia'),
        ('Defensa', 12500.20, datetime.now().strftime('%Y-%m-%d'), 'Presupuestos Estado')
    ]
    
    iniciativas = [
        ('Mejora Línea Autobús Nocturno', 'Transporte', 1250, 'Pendiente', '2026-04-01'),
        ('Ayudas Alquiler Joven', 'Vivienda', 4500, 'En revisión', '2026-04-03'),
        ('Sustitución Importaciones Agrícolas', 'Mercosur', 890, 'Nueva', '2026-04-04')
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO gasto_publico (sector, cantidad, fecha, fuente) VALUES (?, ?, ?, ?)', data_gasto)
    cursor.executemany('INSERT INTO iniciativas (titulo, categoria, votos, estado, fecha_registro) VALUES (?, ?, ?, ?, ?)', iniciativas)
    conn.commit()
    conn.close()

def export_to_json():
    # Exportamos solo lo esencial para el Dashboard (Streamlit/GitHub)
    # Así evitamos subir bases de datos pesadas
    conn = sqlite3.connect(DB_PATH)
    
    # Resumen de gastos
    df_gasto = pd.read_sql_query("SELECT sector, SUM(cantidad) as total FROM gasto_publico GROUP BY sector", conn)
    # Iniciativas populares
    df_iniciativas = pd.read_sql_query("SELECT * FROM iniciativas ORDER BY votos DESC LIMIT 10", conn)
    
    summary = {
        "gastos": df_gasto.to_dict(orient='records'),
        "iniciativas": df_iniciativas.to_dict(orient='records'),
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    with open('/home/dietpi/citizen-watch-osint/data/summary.json', 'w') as f:
        json.dump(summary, f, indent=4)
    
    conn.close()

if __name__ == "__main__":
    init_db()
    fetch_osint_data()
    export_to_json()
    print("OSINT Scraper finalizado con éxito.")
