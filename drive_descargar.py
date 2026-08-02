"""Descarga (SOLO LECTURA) los PDFs nuevos del Drive a las carpetas de entrada.

Estructura en Drive:
  FEM   : Forest Energy Monitor / <anio> / *.pdf          (2 niveles)
  Argus : Argus Biomass Markets / <anio> / <mes> / *.pdf  (3 niveles)

Deja los PDFs en data/pdfs/entrada/{FEM,Argus}/ y luego ingesta.py los carga.
No vuelve a bajar un PDF que ya existe en la carpeta de destino.

Uso:
    uv run python drive_descargar.py            # todos los anios >= 2025
    uv run python drive_descargar.py 2026       # solo un anio (util para ir por tandas)

La autenticacion esta aislada en autenticar(): en la Fase 7, para que corra solo en un
VPS, solo habra que cambiar esa funcion (cuenta de servicio) y nada mas.
"""

import io
import re
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENCIALES = Path("credentials.json")
TOKEN = Path("token.json")
CARPETA_TIPO = "application/vnd.google-apps.folder"
ANIO_DESDE = 2025

DESTINOS = {
    "FEM": Path("data/pdfs/entrada/FEM"),
    "Argus": Path("data/pdfs/entrada/Argus"),
}

# fuente -> (id de carpeta raiz, resourceKey, niveles hasta los PDFs)
FUENTES = {
    "FEM": ("0B2IEeKvuIZtkUy1QaUE3WjJ6Q0U", "0-j1VfwdMvtQSm-bvYeWm2kg", 1),
    "Argus": ("0B2IEeKvuIZtkalZRT0hjdkd1bUE", "0-n5Nk80qLQKw7uncTyZ6JEw", 2),
}

CLAVES: dict[str, str] = {}   # id -> resourceKey (las carpetas 0B... la necesitan)


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


def _cabecera() -> str:
    return ",".join(f"{fid}/{key}" for fid, key in CLAVES.items() if key)


def listar(servicio, carpeta_id: str) -> list[dict]:
    """Lista el contenido de una carpeta y memoriza las resourceKey de los hijos."""
    req = servicio.files().list(
        q=f"'{carpeta_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, resourceKey)",
        pageSize=500,
        orderBy="name",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    )
    cab = _cabecera()
    if cab:
        req.headers["X-Goog-Drive-Resource-Keys"] = cab
    hijos = req.execute().get("files", [])
    for h in hijos:
        if h.get("resourceKey"):
            CLAVES[h["id"]] = h["resourceKey"]
    return hijos


def descargar(servicio, file_id: str, destino: Path) -> None:
    """Baja un archivo. Escribe primero en .parte y renombra al final.

    Asi ingesta.py nunca ve un PDF a medio descargar (que daria error al extraer).
    """
    temporal = destino.with_suffix(destino.suffix + ".parte")
    req = servicio.files().get_media(fileId=file_id, supportsAllDrives=True)
    cab = _cabecera()
    if cab:
        req.headers["X-Goog-Drive-Resource-Keys"] = cab
    with io.FileIO(temporal, "wb") as fh:
        bajador = MediaIoBaseDownload(fh, req)
        hecho = False
        while not hecho:
            _, hecho = bajador.next_chunk()
    temporal.replace(destino)


def _anios(hijos: list[dict], anio_pedido: str | None) -> list[dict]:
    """Carpetas de anio validas: 4 digitos, >= 2025, y el pedido si se indico."""
    out = []
    for h in hijos:
        if h["mimeType"] != CARPETA_TIPO or not re.fullmatch(r"\d{4}", h["name"]):
            continue
        if int(h["name"]) < ANIO_DESDE:
            continue
        if anio_pedido and h["name"] != anio_pedido:
            continue
        out.append(h)
    return out


def _pdfs(hijos: list[dict]) -> list[dict]:
    return [h for h in hijos if h["name"].lower().endswith(".pdf")]


def procesar_fuente(servicio, fuente: str, anio_pedido: str | None) -> int:
    """Baja los PDFs nuevos de una fuente. Devuelve cuantos bajo."""
    raiz, rkey, niveles = FUENTES[fuente]
    CLAVES[raiz] = rkey
    destino_dir = DESTINOS[fuente]
    destino_dir.mkdir(parents=True, exist_ok=True)
    bajados = 0
    for anio in _anios(listar(servicio, raiz), anio_pedido):
        # niveles==1 (FEM): los PDFs estan en el anio. niveles==2 (Argus): en subcarpetas
        contenedores = [anio]
        if niveles == 2:
            contenedores = [c for c in listar(servicio, anio["id"])
                            if c["mimeType"] == CARPETA_TIPO]
        for cont in contenedores:
            for pdf in _pdfs(listar(servicio, cont["id"])):
                ruta = destino_dir / pdf["name"]
                if ruta.exists():
                    continue
                try:
                    descargar(servicio, pdf["id"], ruta)
                    bajados += 1
                    print(f"  {fuente} {anio['name']}: bajado {pdf['name']}")
                except Exception as e:
                    print(f"  {fuente} {anio['name']}: ERROR con {pdf['name']}: {e}")
    return bajados


def main() -> None:
    anio_pedido = sys.argv[1] if len(sys.argv) > 1 else None
    if anio_pedido:
        print(f"(solo anio {anio_pedido})")
    servicio = autenticar()
    total = 0
    for fuente in FUENTES:
        total += procesar_fuente(servicio, fuente, anio_pedido)
    print(f"Descarga terminada: {total} PDFs nuevos.")


if __name__ == "__main__":
    main()
