"""Descarga (SOLO LECTURA) los PDFs nuevos del Drive a las carpetas de entrada.

Estructura en Drive:
  FEM   : Forest Energy Monitor / <anio> / *.pdf          (2 niveles)
  Argus : Argus Biomass Markets / <anio> / <mes> / *.pdf  (3 niveles; tambien acepta
          PDFs sueltos en la carpeta del anio)

Deja los PDFs en data/pdfs/entrada/{FEM,Argus}/ y luego ingesta.py los carga.
No vuelve a bajar un PDF que ya existe en la carpeta de destino.

Uso:
    uv run python drive_descargar.py                    # todos los anios >= 2025
    uv run python drive_descargar.py 2026               # solo un anio
    uv run python drive_descargar.py --saltar-cargados  # no baja lo que ya esta en la BD
                                                        # (lo usa GitHub Actions, que
                                                        #  empieza cada dia sin PDFs)

Autenticacion (autenticar()), por orden:
  1. GOOGLE_SERVICE_ACCOUNT_JSON (variable de entorno con el JSON de la cuenta de servicio)
  2. GOOGLE_TOKEN_JSON           (variable de entorno con el contenido de token.json)
  3. token.json / credentials.json locales (abre el navegador la 1a vez)

Sale con codigo 1 si algun PDF o carpeta da error (asi GitHub Actions avisa por correo).
"""

import io
import json
import os
import re
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
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

CLAVES: dict[str, str] = {}  # id -> resourceKey (las carpetas 0B... la necesitan)


def autenticar():
    """Devuelve el servicio de Drive (ver orden de autenticacion arriba)."""
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    token_json = os.environ.get("GOOGLE_TOKEN_JSON")
    if sa_json:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(sa_json), scopes=SCOPES
        )
    elif token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
        if not creds.valid:
            creds.refresh(Request())
    else:
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
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _cabecera() -> str:
    return ",".join(f"{fid}/{key}" for fid, key in CLAVES.items() if key)


def listar(servicio, carpeta_id: str) -> list[dict]:
    """Lista el contenido de una carpeta (todas las paginas) y memoriza las resourceKey."""
    hijos: list[dict] = []
    token = None
    while True:
        req = servicio.files().list(
            q=f"'{carpeta_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, resourceKey)",
            pageSize=500,
            orderBy="name",
            pageToken=token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        cab = _cabecera()
        if cab:
            req.headers["X-Goog-Drive-Resource-Keys"] = cab
        resp = req.execute()
        hijos += resp.get("files", [])
        token = resp.get("nextPageToken")
        if not token:
            break
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


def _ya_en_bd():
    """Devuelve una funcion (fuente, nombre) -> True si ese PDF ya esta cargado en la BD."""
    from biomass_pipeline.carga import conectar

    from ingesta import _fecha_argus, _issue_fem, claves_en_bd

    with conectar() as conn:
        fechas, issues = claves_en_bd(conn)

    def esta(fuente: str, nombre: str) -> bool:
        try:
            if fuente == "Argus":
                return _fecha_argus(nombre).isoformat() in fechas
            return _issue_fem(nombre) in issues
        except ValueError:
            return False  # nombre raro: se baja y ingesta.py avisara

    return esta


def procesar_fuente(servicio, fuente: str, anio_pedido: str | None, ya_en_bd) -> tuple[int, int]:
    """Baja los PDFs nuevos de una fuente. Devuelve (bajados, errores)."""
    raiz, rkey, niveles = FUENTES[fuente]
    CLAVES[raiz] = rkey
    destino_dir = DESTINOS[fuente]
    destino_dir.mkdir(parents=True, exist_ok=True)
    bajados = errores = 0
    for anio in _anios(listar(servicio, raiz), anio_pedido):
        hijos_anio = listar(servicio, anio["id"])
        # PDFs sueltos en la carpeta del anio (FEM siempre; Argus por si alguien los deja ahi)
        lotes = [_pdfs(hijos_anio)]
        if niveles == 2:
            if lotes[0]:
                print(
                    f"  {fuente} {anio['name']}: (aviso) hay PDFs sueltos fuera de las "
                    "carpetas de mes, los bajo igualmente"
                )
            for cont in hijos_anio:
                if cont["mimeType"] == CARPETA_TIPO:
                    lotes.append(_pdfs(listar(servicio, cont["id"])))
        for lote in lotes:
            for pdf in lote:
                ruta = destino_dir / pdf["name"]
                if ruta.exists() or (ya_en_bd and ya_en_bd(fuente, pdf["name"])):
                    continue
                try:
                    descargar(servicio, pdf["id"], ruta)
                    bajados += 1
                    print(f"  {fuente} {anio['name']}: bajado {pdf['name']}")
                except Exception as e:
                    errores += 1
                    print(f"  {fuente} {anio['name']}: ERROR con {pdf['name']}: {e}")
    return bajados, errores


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    anio_pedido = args[0] if args else None
    if anio_pedido:
        print(f"(solo anio {anio_pedido})")
    ya_en_bd = _ya_en_bd() if "--saltar-cargados" in sys.argv else None
    servicio = autenticar()
    total = errores = 0
    for fuente in FUENTES:
        try:
            b, e = procesar_fuente(servicio, fuente, anio_pedido, ya_en_bd)
            total += b
            errores += e
        except Exception as e:  # p. ej. sin permiso en la carpeta: seguimos con la otra fuente
            errores += 1
            print(f"  {fuente}: ERROR al listar las carpetas: {e}")
    print(f"Descarga terminada: {total} PDFs nuevos, {errores} errores.")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
