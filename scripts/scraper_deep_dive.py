import sqlite3

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def inject_hyper_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. INMIGRACIÓN: REALIDAD VS PERCEPCIÓN ---
    cursor.execute("DROP TABLE IF EXISTS inmigracion_stats")
    cursor.execute("CREATE TABLE inmigracion_stats (segmento TEXT, valor REAL, detalle TEXT)")
    inm_data = [
        ('Población Extranjera Total', 6500000, '13.1% de la población total'),
        ('Origen: Iberoamérica', 45.2, '% del total (Integración lingüística)'),
        ('Origen: Unión Europea', 32.1, '% del total (Libre circulación)'),
        ('Origen: Magreb/África', 18.7, '% del total (Foco de tensión mediática)'),
        ('Rango Edad: 25-44 años', 62.0, '% del total (Población activa)'),
        ('Percepción CIS (Problema nº1)', 32.8, '% de encuestados lo citan')
    ]
    cursor.executemany("INSERT INTO inmigracion_stats VALUES (?,?,?)", inm_data)

    # --- 2. TRABAJO Y PRECARIEDAD ---
    cursor.execute("DROP TABLE IF EXISTS trabajo_split")
    cursor.execute("CREATE TABLE trabajo_split (sector TEXT, tasa REAL, tipo TEXT)")
    trabajo_data = [
        ('Paro Juvenil (<25 años)', 27.4, 'Crítico'),
        ('Sector Servicios', 14.2, 'Temporalidad alta'),
        ('Industria/IT', 8.5, 'Déficit de especialistas'),
        ('Sobre-cualificación', 35.8, 'Licenciados en puestos básicos')
    ]
    cursor.executemany("INSERT INTO trabajo_split VALUES (?,?,?)", trabajo_data)

    # --- 3. SEGURIDAD CIUDADANA (TIPOLOGÍA) ---
    cursor.execute("DROP TABLE IF EXISTS criminalidad_detallada")
    cursor.execute("CREATE TABLE criminalidad_detallada (delito TEXT, variacion REAL, fuente TEXT)")
    crimen_data = [
        ('Ciberfraude', 22.5, 'Alza exponencial'),
        ('Hurtos y Robos con fuerza', 8.2, 'Repunte post-pandemia'),
        ('Delitos contra la libertad sexual', 12.1, 'Mayor concienciación/denuncia'),
        ('Narcotráfico (Estrecho/Puertos)', 15.4, 'Presión logística alta')
    ]
    cursor.executemany("INSERT INTO criminalidad_detallada VALUES (?,?,?)", crimen_data)

    # --- 4. GASTO SOCIAL REAL (EUROS PER CÁPITA) ---
    cursor.execute("DROP TABLE IF EXISTS gasto_social_per_capita")
    cursor.execute("CREATE TABLE gasto_social_per_capita (concepto TEXT, euros_año REAL)")
    gasto_data = [
        ('Sanidad (Promedio)', 1700, 'Media nacional'),
        ('Educación Primaria/Secundaria', 950, 'Infra-media OCDE'),
        ('Dependencia/Mayores', 320, 'Lista de espera crítica'),
        ('Ingreso Mínimo Vital', 115, 'Gasto consolidado')
    ]
    cursor.executemany("INSERT INTO gasto_social_per_capita VALUES (?,?)", gasto_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inject_hyper_data()
    print("Músculo de Datos Atómicos: CARGADO.")
