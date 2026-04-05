import sqlite3
import os

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def optimize_db():
    conn = sqlite3.connect(DB_PATH)
    # Limpia espacio de registros eliminados y compacta el archivo
    conn.execute("VACUUM")
    # Analiza para optimizar planes de consulta
    conn.execute("ANALYZE")
    conn.close()
    print("Base de datos optimizada.")

def clean_old_data(days=30):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Borrar datos OSINT de más de 30 días para no saturar la eMMC/SD
    cursor.execute(f"DELETE FROM observations WHERE date < date('now', '-{days} days')")
    conn.commit()
    conn.close()
    optimize_db()

if __name__ == "__main__":
    clean_old_data()
