"""Proveedor de IA del centro (openai-compatible) con urllib, sin dependencias extra."""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path

from tareas.errores import IaError

_MODELO_DEFECTO = "Qwen38-DualSpark-medium"


def _ca_context() -> ssl.SSLContext:
    ca = os.environ.get("CENTRO_IA_CA")
    if not ca:
        p = Path.home() / ".config" / "opencode" / "ca-simarro.crt"
        ca = str(p) if p.exists() else None
    return ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()


def _url() -> str:
    url = os.environ.get("CENTRO_IA_URL")
    if not url:
        raise IaError("IA no disponible: falta CENTRO_IA_URL (modo sin red).")
    return url.rstrip("/")


def _key() -> str:
    key = os.environ.get("CENTRO_IA_KEY")
    if not key:
        raise IaError("IA no disponible: falta CENTRO_IA_KEY (modo sin red).")
    return key


def disponible() -> bool:
    return bool(os.environ.get("CENTRO_IA_URL") and os.environ.get("CENTRO_IA_KEY"))


def _post(payload: dict) -> str:
    req = urllib.request.Request(
        _url() + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + _key()},
    )
    try:
        with urllib.request.urlopen(req, timeout=180, context=_ca_context()) as r:
            cuerpo = json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise IaError(f"Sin conexion con la IA del centro ({getattr(exc, 'reason', exc)}).") from None
    except TimeoutError:
        raise IaError("Tiempo de espera agotado con la IA del centro.") from None
    try:
        return cuerpo["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise IaError("Respuesta inesperada del servidor de IA.") from None


def completar(mensaje: str, system: str = "Eres un asistente util.") -> str:
    if not disponible():
        raise IaError("IA no disponible: faltan CENTRO_IA_URL/CENTRO_IA_KEY (modo sin red).")
    payload = {
        "model": os.environ.get("TAREAS_MODELO_IA", _MODELO_DEFECTO),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": mensaje}],
    }
    return _post(payload)


def resumir(texto: str) -> str:
    return completar("Resume en 5 puntos clave este documento:\n\n" + texto[:8000],
                     system="Resume de forma concisa en espanol.")


def nombre_sugerido(texto: str) -> str:
    return completar("Propone un nombre de fichero corto, minusculas, con guiones, sin extension, "
                     "que describa el contenido:\n\n" + texto[:2000],
                     system="Devuelve solo el nombre, sin comillas.")