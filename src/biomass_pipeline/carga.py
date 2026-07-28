"""Carga de datos extraidos a PostgreSQL con upsert (insertar o actualizar).

Reprocesar el mismo PDF NO duplica: si la clave ya existe, actualiza la fila.
La conexion se lee de DATABASE_URL (.env), nunca del codigo.
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Abre una conexion a la base de datos usando DATABASE_URL del .env."""
    return psycopg.connect(os.environ["DATABASE_URL"])


def upsert(conn, tabla: str, clave: list[str], fila: dict) -> None:
    """Inserta 'fila' en 'tabla'. Si la 'clave' ya existe, actualiza en vez de duplicar."""
    cols = list(fila.keys())
    valores = [fila[c] for c in cols]
    marcadores = ", ".join(["%s"] * len(cols))
    lista_cols = ", ".join(cols)
    actualizaciones = ", ".join(f"{c} = excluded.{c}" for c in cols if c not in clave)
    conflicto = ", ".join(clave)
    sql = (
        f"insert into {tabla} ({lista_cols}) values ({marcadores}) "
        f"on conflict ({conflicto}) do update set {actualizaciones}"
    )
    with conn.cursor() as cur:
        cur.execute(sql, valores)
    conn.commit()
