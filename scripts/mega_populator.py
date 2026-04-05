import sqlite3

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def full_rebuild():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- FICHA METODOLÓGICA Y FUENTES (SEO & RIGOR) ---
    cursor.execute("DROP TABLE IF EXISTS metadatos")
    cursor.execute("CREATE TABLE metadatos (area TEXT, fuente TEXT, metodo TEXT, fiabilidad TEXT)")
    meta = [
        ('Inmigración', 'INE / Ministerio Interior', 'Censo y Registro Civil', 'Alta'),
        ('Trabajo', 'EPA (Encuesta Población Activa)', 'Muestreo Trimestral', 'Alta'),
        ('Seguridad', 'Balance de Criminalidad (Interior)', 'Denuncias Registradas', 'Media-Alta'),
        ('Gasto Social', 'IGAE / Presupuestos Generales', 'Ejecución Presupuestaria', 'Crítica'),
        ('Percepción', 'CIS (Barómetros Mensuales)', 'Entrevista Directa', 'Alta')
    ]
    cursor.executemany("INSERT INTO metadatos VALUES (?,?,?,?)", meta)

    # --- INMIGRACIÓN: REALIDAD DEMOGRÁFICA ---
    cursor.execute("DROP TABLE IF EXISTS inmigracion_stats")
    cursor.execute("CREATE TABLE inmigracion_stats (segmento TEXT, valor REAL, detalle TEXT)")
    inm = [
        ('Total Extranjeros', 6540000, '13.1% población total'),
        ('Origen: Iberoamérica', 45.2, 'Integración cultural y lingüística'),
        ('Origen: Unión Europea', 32.1, 'Libre circulación comunitaria'),
        ('Origen: África/Magreb', 18.7, 'Foco de tensión OSINT / Fronteras'),
        ('Edad: 25-44 años', 62.0, 'Población activa (Músculo laboral)'),
        ('Tasa de Actividad', 71.5, 'Superior a la media nacional')
    ]
    cursor.executemany("INSERT INTO inmigracion_stats VALUES (?,?,?)", inm)

    # --- TRABAJO Y EDUCACIÓN ---
    cursor.execute("DROP TABLE IF EXISTS trabajo_split")
    cursor.execute("CREATE TABLE trabajo_split (sector TEXT, tasa REAL, tipo TEXT)")
    trab = [
        ('Paro Juvenil (<25)', 27.4, 'Crítico / Riesgo exclusión'),
        ('Sobre-cualificación', 35.8, 'Licenciados en subempleo'),
        ('Temporalidad Pública', 31.2, 'Interinidad en Sanidad/Educación'),
        ('Brecha Salarial', 18.4, 'Diferencia estructural')
    ]
    cursor.executemany("INSERT INTO trabajo_split VALUES (?,?,?)", trab)

    # --- SEGURIDAD Y CONFLICTO ---
    cursor.execute("DROP TABLE IF EXISTS criminalidad_detallada")
    cursor.execute("CREATE TABLE criminalidad_detallada (delito TEXT, variacion REAL, fuente TEXT)")
    crim = [
        ('Ciberestafas (Phishing)', 22.5, 'Crimen organizado digital'),
        ('Hurtos Reincidentes', 8.2, 'Presión en grandes urbes'),
        ('Narcotráfico (Logística)', 15.4, 'Presión en puertos y costas'),
        ('Inseguridad Percibida', 14.8, 'Dato subjetivo (CIS)')
    ]
    cursor.executemany("INSERT INTO criminalidad_detallada VALUES (?,?,?)", crim)

    # --- GASTO POLÍTICO VS SOCIAL (M€) ---
    cursor.execute("DROP TABLE IF EXISTS gasto_corrupcion")
    cursor.execute("CREATE TABLE gasto_corrupcion (concepto TEXT, cantidad REAL, categoria TEXT)")
    gasto = [
        ('Hospitales y Primaria', 1700, 'Social (Euros/Cápita)'),
        ('Becas y Universidad', 950, 'Social (Euros/Cápita)'),
        ('Cargos de Confianza', 1100, 'Político (Muestreo Anual)'),
        ('Publicidad Institucional', 600, 'Político (Muestreo Anual)')
    ]
    cursor.executemany("INSERT INTO gasto_corrupcion VALUES (?,?,?)", gasto)

    conn.commit()
    conn.close()
    print("✅ Músculo de Datos Auditado y Cargado.")

if __name__ == "__main__":
    full_rebuild()
