import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def _get_supabase_url() -> str:
    return (
        getattr(settings, "SUPABASE_URL", "")
        or os.getenv("SUPABASE_URL", "")
        or os.getenv("EXPO_PUBLIC_SUPABASE_URL", "")
    ).rstrip("/")


def _get_supabase_key() -> str:
    return (
        getattr(settings, "SUPABASE_ANON_KEY", "")
        or getattr(settings, "SUPABASE_KEY", "")
        or os.getenv("SUPABASE_ANON_KEY", "")
        or os.getenv("SUPABASE_KEY", "")
        or os.getenv("EXPO_PUBLIC_SUPABASE_ANON_KEY", "")
    )


def _get_timeout_seconds() -> int:
    timeout = (
        getattr(settings, "SUPABASE_TIMEOUT_SECONDS", None)
        or os.getenv("SUPABASE_TIMEOUT_SECONDS", "")
        or "12"
    )
    try:
        return int(timeout)
    except Exception:
        return 12


def _get_service_role_key() -> str:
    return (
        getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    )


def _build_headers() -> Dict[str, str]:
    key = _get_supabase_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }


def _base_url() -> str:
    supabase_url = _get_supabase_url()
    return f"{supabase_url}/rest/v1"


def _is_ready() -> bool:
    supabase_url = _get_supabase_url()
    supabase_key = _get_supabase_key()
    return bool(supabase_url and supabase_key)


def _fetch_instituciones() -> Dict[int, str]:
    if not _is_ready():
        return {}

    url = f"{_base_url()}/instituciones"
    params = {
        "select": "id,nombre",
        "limit": "2000",
    }
    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            params=params,
            timeout=_get_timeout_seconds(),
        )
        response.raise_for_status()
        rows = response.json() or []
        return {int(row["id"]): row.get("nombre", "") for row in rows if row.get("id") is not None}
    except Exception:
        logger.exception("No se pudo obtener instituciones desde Supabase")
        return {}


def fetch_relevamientos(
    limit: int = 200,
    sync_estado: Optional[str] = None,
    query: Optional[str] = None,
    institucion_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not _is_ready():
        return {
            "success": False,
            "error": "Falta configurar SUPABASE_URL y SUPABASE_ANON_KEY (o EXPO_PUBLIC_SUPABASE_*) en .env",
            "items": [],
        }

    url = f"{_base_url()}/relevamientos"
    params: Dict[str, str] = {
        "select": (
            "id,client_uid,id_institucion,"
            "responsable_nombre,responsable_apellido,responsable_dni,responsable_telefono,responsable_email,responsable_funcion,"
            "latitud,longitud,observaciones,sync_estado,sync_error,last_synced_at,relevado_at,created_at,updated_at,created_by,usuario_username"
        ),
        "order": "created_at.desc",
        "limit": str(limit),
        "deleted_at": "is.null",
    }

    if sync_estado:
        params["sync_estado"] = f"eq.{sync_estado}"

    if institucion_id:
        params["id_institucion"] = f"eq.{institucion_id}"

    if query:
        q = query.replace("*", "").strip()
        if q:
            params["or"] = (
                f"(responsable_nombre.ilike.*{q}*,"
                f"responsable_apellido.ilike.*{q}*,"
                f"responsable_dni.ilike.*{q}*)"
            )

    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            params=params,
            timeout=_get_timeout_seconds(),
        )
        response.raise_for_status()
        rows: List[Dict[str, Any]] = response.json() or []
    except requests.RequestException as exc:
        logger.exception("Error consultando relevamientos en Supabase")
        return {
            "success": False,
            "error": f"No se pudo consultar Supabase: {exc}",
            "items": [],
        }

    instituciones = _fetch_instituciones()
    for row in rows:
        institucion_id = row.get("id_institucion")
        row["institucion_nombre"] = instituciones.get(institucion_id, f"Institucion #{institucion_id}") if institucion_id else "-"

    return {
        "success": True,
        "error": "",
        "items": rows,
    }


def fetch_instituciones_list() -> List[Dict[str, Any]]:
    if not _is_ready():
        return []

    url = f"{_base_url()}/instituciones"
    params = {
        "select": "id,nombre",
        "order": "nombre.asc",
        "limit": "2000",
    }
    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            params=params,
            timeout=_get_timeout_seconds(),
        )
        response.raise_for_status()
        return response.json() or []
    except requests.RequestException:
        logger.exception("Error consultando instituciones en Supabase")
        return []


def fetch_adjuntos_counts(relevamiento_ids: List[str]) -> Dict[str, int]:
    if not _is_ready() or not relevamiento_ids:
        return {}

    ids = ",".join(relevamiento_ids)
    url = f"{_base_url()}/relevamiento_adjuntos"
    params = {
        "select": "relevamiento_id",
        "relevamiento_id": f"in.({ids})",
    }

    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            params=params,
            timeout=_get_timeout_seconds(),
        )
        response.raise_for_status()
        rows: List[Dict[str, Any]] = response.json() or []
    except requests.RequestException:
        logger.exception("Error consultando adjuntos en Supabase")
        return {}

    counts: Dict[str, int] = {}
    for row in rows:
        rid = row.get("relevamiento_id")
        if not rid:
            continue
        counts[rid] = counts.get(rid, 0) + 1
    return counts


def fetch_relevamiento_detail(relevamiento_id: str) -> Dict[str, Any]:
    if not _is_ready():
        return {"success": False, "error": "Supabase no configurado", "item": None, "adjuntos": [], "campos_extra": []}

    base = _base_url()
    headers = _build_headers()
    timeout = _get_timeout_seconds()

    item_url = f"{base}/relevamientos"
    item_params = {
        "select": "*",
        "id": f"eq.{relevamiento_id}",
        "limit": "1",
    }

    adjuntos_url = f"{base}/relevamiento_adjuntos"
    adjuntos_params = {
        "select": "id,categoria,tipo_archivo,nombre_original,mime_type,size_bytes,storage_bucket,storage_path,created_at",
        "relevamiento_id": f"eq.{relevamiento_id}",
        "order": "created_at.desc",
    }

    extras_url = f"{base}/relevamiento_campos_extra"
    extras_params = {
        "select": "id,orden,nombre,valor,created_at",
        "relevamiento_id": f"eq.{relevamiento_id}",
        "order": "orden.asc",
    }

    try:
        item_resp = requests.get(item_url, headers=headers, params=item_params, timeout=timeout)
        item_resp.raise_for_status()
        item_rows = item_resp.json() or []
        item = item_rows[0] if item_rows else None
        if not item:
            return {"success": False, "error": "No se encontro el relevamiento solicitado", "item": None, "adjuntos": [], "campos_extra": []}

        adjuntos_resp = requests.get(adjuntos_url, headers=headers, params=adjuntos_params, timeout=timeout)
        adjuntos_resp.raise_for_status()
        adjuntos = adjuntos_resp.json() or []

        extras_resp = requests.get(extras_url, headers=headers, params=extras_params, timeout=timeout)
        extras_resp.raise_for_status()
        campos_extra = extras_resp.json() or []
    except requests.RequestException as exc:
        logger.exception("Error consultando detalle de relevamiento en Supabase")
        return {"success": False, "error": f"No se pudo consultar Supabase: {exc}", "item": None, "adjuntos": [], "campos_extra": []}

    instituciones = _fetch_instituciones()
    institucion_id = item.get("id_institucion")
    item["institucion_nombre"] = instituciones.get(institucion_id, f"Institucion #{institucion_id}") if institucion_id else "-"

    return {
        "success": True,
        "error": "",
        "item": item,
        "adjuntos": adjuntos,
        "campos_extra": campos_extra,
    }


def fetch_username_by_user_id(user_id: Optional[str]) -> str:
    """Resuelve username de auth.users por UUID usando Supabase Admin API."""
    if not user_id:
        return "-"

    supabase_url = _get_supabase_url()
    service_key = _get_service_role_key()
    if not (supabase_url and service_key):
        return user_id

    url = f"{supabase_url}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=_get_timeout_seconds())
        response.raise_for_status()
        payload = response.json() or {}
        user = payload.get("user") if isinstance(payload, dict) else None
        if not user:
            return user_id

        user_metadata = user.get("user_metadata") or {}
        raw_meta = user.get("raw_user_meta_data") or {}
        username = (
            user_metadata.get("username")
            or raw_meta.get("username")
            or user_metadata.get("name")
            or raw_meta.get("name")
        )
        if username:
            return str(username)

        email = user.get("email")
        if email and "@" in email:
            return email.split("@", 1)[0]
        return user_id
    except requests.RequestException:
        logger.exception("No se pudo resolver username en Supabase para user_id=%s", user_id)
        return user_id


def fetch_usernames_by_user_ids(user_ids: List[str]) -> Dict[str, str]:
    """Resuelve varios user_id -> username con cache simple en memoria."""
    resolved: Dict[str, str] = {}
    for user_id in set([uid for uid in user_ids if uid]):
        resolved[user_id] = fetch_username_by_user_id(user_id)
    return resolved


def get_storage_public_url(storage_path: Optional[str], bucket: str = "relevamientos") -> str:
    if not storage_path:
        return ""
    if str(storage_path).startswith("http://") or str(storage_path).startswith("https://"):
        return str(storage_path)
    # Rutas locales de mobile no son accesibles desde web.
    if str(storage_path).startswith("file://") or str(storage_path).startswith("content://"):
        return ""
    supabase_url = _get_supabase_url()
    if not supabase_url:
        return ""
    safe_path = quote(storage_path.lstrip("/"), safe="/")
    return f"{supabase_url}/storage/v1/object/public/{bucket}/{safe_path}"


def get_storage_signed_url(storage_path: Optional[str], bucket: str = "relevamientos", expires_in: int = 3600) -> str:
    if not storage_path:
        return ""
    if str(storage_path).startswith("http://") or str(storage_path).startswith("https://"):
        return str(storage_path)
    if str(storage_path).startswith("file://") or str(storage_path).startswith("content://"):
        return ""

    supabase_url = _get_supabase_url()
    key = _get_service_role_key() or _get_supabase_key()
    if not (supabase_url and key):
        return get_storage_public_url(storage_path, bucket=bucket)

    safe_path = quote(storage_path.lstrip("/"), safe="/")
    url = f"{supabase_url}/storage/v1/object/sign/{bucket}/{safe_path}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"expiresIn": int(expires_in)},
            timeout=_get_timeout_seconds(),
        )
        response.raise_for_status()
        payload = response.json() or {}
        signed = payload.get("signedURL") or payload.get("signedUrl") or ""
        if signed.startswith("http://") or signed.startswith("https://"):
            return signed
        if signed:
            return f"{supabase_url}/storage/v1{signed}"
        return get_storage_public_url(storage_path, bucket=bucket)
    except requests.RequestException:
        logger.exception("No se pudo generar signed URL para storage_path=%s", storage_path)
        return get_storage_public_url(storage_path, bucket=bucket)
