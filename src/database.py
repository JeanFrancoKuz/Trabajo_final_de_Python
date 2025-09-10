import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.getenv("DATABASE", os.path.join(BASE_DIR, "ecommerce.db"))

def get_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas como diccionarios
    return conn

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Tabla usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            edad INTEGER NOT NULL,
            telefono TEXT UNIQUE,
            correo TEXT UNIQUE,
            clave_hash TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            pais TEXT NOT NULL,
            registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Tabla productos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL,
            stock INTEGER NOT NULL,
            registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Tabla ventas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES productos (id)
        )
        ''')

        conn.commit()
        print(f"Base de datos inicializada en {db_path}")

    except Exception as e:
        print(f"Error al inicializar la DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
