"""Explora las carpetas de Google Drive (SOLO LECTURA) para ver como estan organizadas.

La primera vez abre el navegador para que autorices con tu cuenta de Google; despues
guarda token.json y ya no vuelve a preguntar. token.json es SECRETO (no subir a git).

Lista los anios de cada fuente y, para los de 2025 en adelante, entra a ver que hay
dentro (PDFs directos? mas subcarpetas?).

La autenticacion esta aislada en autenticar(): en la Fase 7, para que corra solo en un
VPS, solo habra que cambiar esa funcion (cuenta de servicio) y nada mas.

Uso:
    uv run python drive_explorar.py
"""

import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENCIALES = Path("credentials.json")
TOKEN = Path("token.json")
CARPETA_TIPO = "application/vnd.google-apps.folder"
ANIO_DESDE = 2025

# nombre -> (id de carpeta, resourceKey del enlace compartido)
CARPETAS = {
    "FEM": ("0B2IEeKvuIZtkUy1QaUE3WjJ6Q0U", "0-j1VfwdMvtQSm-bvYeWm2kg"),
    "Argus": ("0B2IEeKvuIZtkalZRT0hjdkd1bUE", "0-n5Nk80qLQKw7uncTyZ6JEw"),
}

# las carpetas antiguas (id 0B...) necesitan su resourceKey; se van acumulando aqui
CLAVES: dict[str, str] = {}


def autenticar():
    """Devuelve el servicio de Drive. La 1a vez abre el navegador para autorizar."""
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENCIALES), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds)


def _cabecera_claves() -> str:
    """Cabecera con todas las resourceKey conocidas: 'id1/clave1,id2/clave2'."""
    return ",".join(f"{fid}/{key}" for fid, key in CLAVES.items() if key)


def listar(servicio, carpeta_id: str) -> list[dict]:
    """Lista lo que hay dentro de una carpeta: nombre, tipo, id y resourceKey."""
    req = servicio.files().list(
        q=f"'{carpeta_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, resourceKey)",
        pageSize=500,
        orderBy="name",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    )
    cabecera = _cabecera_claves()
    if cabecera:
        req.headers["X-Goog-Drive-Resource-Keys"] = cabecera
    hijos = req.execute().get("files", [])
    for h in hijos:  # guardar claves de los hijos para poder entrar en ellos
        if h.get("resourceKey"):
            CLAVES[h["id"]] = h["resourceKey"]
    return hijos


def _es_anio_reciente(nombre: str) -> bool:
    return bool(re.fullmatch(r"\d{4}", nombre)) and int(nombre) >= ANIO_DESDE


def main() -> None:
    servicio = autenticar()
    for fuente, (cid, rkey) in CARPETAS.items():
        CLAVES[cid] = rkey
        print(f"\n================ {fuente} ================")
        try:
            hijos = listar(servicio, cid)
        except Exception as e:
            print(f"  ERROR listando la raiz: {e}")
            continue
        anios = [h for h in hijos if h["mimeType"] == CARPETA_TIPO]
        print(f"  carpetas encontradas: {', '.join(h['name'] for h in anios)}")
        for anio in anios:
            if not _es_anio_reciente(anio["name"]):
                continue
            print(f"\n  --- {fuente} / {anio['name']} ---")
            try:
                dentro = listar(servicio, anio["id"])
            except Exception as e:
                print(f"    ERROR: {e}")
                continue
            if not dentro:
                print("    (vacia)")
            for f in dentro[:15]:  # primeros 15, para no inundar la pantalla
                es_carp = f["mimeType"] == CARPETA_TIPO
                print(f"    [{'CARPETA' if es_carp else 'archivo'}] {f['name']}")
            if len(dentro) > 15:
                print(f"    ... y {len(dentro) - 15} mas (total {len(dentro)})")


if __name__ == "__main__":
    main()
