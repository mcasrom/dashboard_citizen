import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def inject_atomic_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. METODOLOGÍA Y FUENTES (Para el SEO y Veracidad)
    cursor.execute("DROP TABLE IF EXISTS metadata_sources")
    cursor.execute("CREATE TABLE metadata_sources (area TEXT, fuente TEXT, fiabilidad TEXT, metodo TEXT)")
    sources = [
        ('Sanidad/Salud', 'Ministerio de Sanidad / SESPAS', 'Alta', 'Extracción API Datos Abiertos'),
        ('Seguridad/Inmigración', 'Ministerio Interior / Frontex', 'Media-Alta', 'Scraping BOE / Notas de Prensa'),
        ('Mercosur/Alimentos', 'RASFF (EU) / EFSA', 'Crítica', 'OSINT: Alertas Fitosanitarias'),
        ('Inquietudes', 'CIS (Barómetros Mensuales)', 'Alta', 'Análisis de Series Temporales'),
        ('Transporte', 'ADIF / Renfe Operadora', 'Media', 'Análisis de Retrasos y Licitaciones')
    ]
    cursor.executemany("INSERT INTO metadata_sources VALUES (?,?,?,?)", sources)

    # 2. SPLIT DE GASTO DETALLADO (M€)
    cursor.execute("DROP TABLE IF EXISTS pge_split")
    cursor.execute("CREATE TABLE pge_split (categoria TEXT, subsector TEXT, cantidad REAL, tendencia TEXT)")
    splits = [
        ('Salud', 'Atención Primaria', 12400, 'Infrapresupuestado'),
        ('Salud', 'Gasto Hospitalario', 48000, 'Alza por Cronicidad'),
        ('Salud', 'Salud Mental', 450, 'Crítico/Insuficiente'),
        ('Defensa', 'Programas Especiales Armamento', 8200, 'Incremento OTAN'),
        ('Defensa', 'Misiones Internacionales', 1200, 'Estable'),
        ('Transporte', 'Cercanías (Mantenimiento)', 2100, 'Déficit Histórico'),
        ('Transporte', 'Alta Velocidad (Inversión)', 5800, 'Prioridad Política'),
        ('Trabajo', 'Subsidios Desempleo', 18000, 'Estructural'),
        ('Trabajo', 'Formación y Empleo Joven', 1500, 'Baja Ejecución'),
        ('Inmigración', 'Salvamento Marítimo', 240, 'Saturado'),
        ('Inmigración', 'Centros de Estancia Temporal', 1100, 'Desbordado')
    ]
    cursor.executemany("INSERT INTO pge_split VALUES (?,?,?,?)", splits)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inject_atomic_data()
    print("Músculo atómico cargado en ODROID-C2.")
