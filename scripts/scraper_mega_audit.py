import sqlite3
import pandas as pd

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def mega_injection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. MATRIZ DE GASTO DETALLADO (SPLIT TOTAL) ---
    cursor.execute("DROP TABLE IF EXISTS audit_pro")
    cursor.execute("CREATE TABLE audit_pro (area TEXT, subsector TEXT, cantidad REAL, nota TEXT)")
    
    data = [
        ('Salud', 'Atención Primaria', 12000, 'Déficit estructural'),
        ('Salud', 'Salud Mental', 450, 'Crítico: < 1% total'),
        ('Salud', 'Gasto Farmacéutico', 18000, 'Alza descontrolada'),
        ('Defensa', 'Modernización F-35/Eurofighter', 4500, 'Compromiso OTAN'),
        ('Defensa', 'Personal y Tropa', 5500, 'Sueldos congelados'),
        ('Educación', 'Becas Comedor/Libros', 1200, 'Insuficiente'),
        ('Educación', 'I+D Universitaria', 900, 'Fuga de cerebros'),
        ('Transporte', 'Cercanías (Mantenimiento)', 850, 'Frecuentes averías'),
        ('Transporte', 'Alta Velocidad (AVE)', 6200, 'Inversión política'),
        ('Seguridad', 'Inmigración (Control)', 2100, 'Saturación fronteriza'),
        ('Seguridad', 'Inmigración (Integración)', 400, 'Mínimo histórico'),
        ('Política', 'Cargos de Confianza / Asesores', 1100, 'Récord histórico'),
        ('Política', 'Publicidad Institucional', 600, 'Control mediático')
    ]
    cursor.executemany("INSERT INTO audit_pro VALUES (?,?,?,?)", data)

    # --- 2. BARÓMETRO CIS Y TENSIÓN SOCIAL ---
    cursor.execute("DROP TABLE IF EXISTS cis_tension")
    cursor.execute("CREATE TABLE cis_tension (problema TEXT, preocupacion REAL, tendencia TEXT)")
    
    cis = [
        ('Inmigración', 32.8, 'En ascenso'),
        ('Vivienda (Alquileres)', 29.5, 'Crítico'),
        ('Corrupción Política', 24.1, 'Sistémico'),
        ('Paro Juvenil', 27.2, 'Estructural'),
        ('Sanidad Pública', 19.4, 'Deterioro percibido'),
        ('Inseguridad', 14.8, 'Creciente')
    ]
    cursor.executemany("INSERT INTO cis_tension VALUES (?,?,?)", cis)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    mega_injection()
    print("Músculo de Auditoría Total Inyectado.")
