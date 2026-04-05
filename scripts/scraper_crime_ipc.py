import sqlite3
from datetime import datetime

DB_PATH = '/home/dietpi/citizen-watch-osint/data/citizen_data.db'

def update_social_friction():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Correlación: Subida IPC Alimentos vs Inseguridad Percibida
    friction_data = [
        ('Aceite de Oliva (IPC +150%)', 'Precios', 2025),
        ('Cesta Básica (IPC +22%)', 'Precios', 2025),
        ('Hurtos en Superficies Comerciales', 'Inseguridad', 2025),
        ('Vandalismo en Transporte Público', 'Inseguridad', 2025)
    ]

    cursor.execute("DROP TABLE IF EXISTS social_friction")
    cursor.execute("CREATE TABLE social_friction (evento TEXT, categoria TEXT, año INTEGER)")
    cursor.executemany("INSERT INTO social_friction VALUES (?,?,?)", friction_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_social_friction()
    print("Métrica de Fricción Social cargada.")
