import sqlite3

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def inject_mega_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- TABLA: PRESUPUESTOS Y GASTO DETALLADO (M€) ---
    cursor.execute("DROP TABLE IF EXISTS pge_audit")
    cursor.execute("CREATE TABLE pge_audit (area TEXT, subsector TEXT, cantidad REAL, estado TEXT)")
    pge_data = [
        ('Salud', 'Hospitales y Especializada', 55000, 'Ejecutado'),
        ('Salud', 'Atención Primaria', 12000, 'Infrapresupuestado'),
        ('Defensa', 'Programas de Armamento', 7500, 'Aumento 15%'),
        ('Defensa', 'Personal y Operaciones', 6000, 'Estable'),
        ('Educación', 'Becas y Ayudas', 2500, 'Insuficiente'),
        ('Educación', 'Universidad e I+D', 1800, 'Congelado'),
        ('Transporte', 'Cercanías y Red Convencional', 3200, 'Crisis de mantenimiento'),
        ('Transporte', 'Alta Velocidad (AVE)', 5400, 'Sobrepago'),
        ('Trabajo', 'Políticas Activas de Empleo', 6500, 'Baja eficiencia'),
        ('Seguridad', 'Cuerpos y Fuerzas de Seguridad', 9500, 'Saturado'),
        ('Inmigración', 'Centros de Acogida y Fronteras', 3800, 'Desbordado')
    ]
    cursor.executemany("INSERT INTO pge_audit VALUES (?,?,?,?)", pge_data)

    # --- TABLA: INDICADORES DE TENSIÓN CIUDADANA (CIS + OSINT) ---
    cursor.execute("DROP TABLE IF EXISTS tension_social")
    cursor.execute("CREATE TABLE tension_social (indicador TEXT, valor REAL, tendencia TEXT, fuente TEXT)")
    tension_data = [
        ('Preocupación Inmigración', 32.5, 'Alza Crítica', 'CIS'),
        ('Inseguridad Ciudadana', 15.2, 'Creciente', 'OSINT/Policial'),
        ('Dificultad Acceso Vivienda', 42.1, 'Máximo Histórico', 'Idealista/CIS'),
        ('Desafección Clase Política', 38.9, 'Récord', 'CIS'),
        ('Precariedad Laboral (Juvenil)', 29.4, 'Estancado', 'EPA'),
        ('Listas de Espera Quirúrgica', 180, 'Días (Media)', 'Sanidad')
    ]
    cursor.executemany("INSERT INTO tension_social VALUES (?,?,?,?)", tension_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inject_mega_data()
    print("Músculo de Auditoría PGE/CIS cargado.")
