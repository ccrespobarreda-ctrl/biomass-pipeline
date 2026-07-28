"""Prueba de conexion a la base de datos. No mete ni lee datos: solo comprueba
que la llave (DATABASE_URL del .env) funciona y que la red deja conectar."""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env

url = os.environ["DATABASE_URL"]

try:
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from argus_semanal;")
            filas = cur.fetchone()[0]
    print("CONEXION OK. La tabla argus_semanal tiene", filas, "filas.")
except Exception as e:
    print("FALLO LA CONEXION:")
    print(e)