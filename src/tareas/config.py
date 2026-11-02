"""Lectura y validacion de acciones.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tareas.errores import ConfigError

TIPOS_VALIDOS = {"mover", "renombrar", "copiar", "borrar", "ia-resumir", "ia-renombrar"}
_NOMBRE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _validar_filtro(filtro: Any, ruta: str, errores: list[str]) -> None:
    if not isinstance(filtro, dict):
        errores.append(f"{ruta}: 'filtro' debe ser un objeto")
        return
    permitidas = {"extensiones", "patron", "mas_antiguo_que_dias"}
    desconocidas = set(filtro) - permitidas
    if desconocidas:
        errores.append(f"{ruta}: claves de filtro desconocidas: {sorted(desconocidas)}")
    if "extensiones" in filtro:
        ext = filtro["extensiones"]
        ok = isinstance(ext, list) and ext and all(isinstance(e, str) and e.startswith(".") for e in ext)
        if not ok:
            errores.append(f"{ruta}.filtro.extensiones: lista no vacia de extensiones con '.' (p.ej. '.pdf')")
    if "patron" in filtro:
        p = filtro["patron"]
        if not isinstance(p, str):
            errores.append(f"{ruta}.filtro.patron: debe ser texto")
        else:
            try:
                re.compile(p)
            except re.error as exc:
                errores.append(f"{ruta}.filtro.patron: regex invalida ({exc})")
    if "mas_antiguo_que_dias" in filtro:
        n = filtro["mas_antiguo_que_dias"]
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            errores.append(f"{ruta}.filtro.mas_antiguo_que_dias: entero >= 0")


def _validar_accion(a: Any, i: int, nombres: set[str], errores: list[str]) -> None:
    ruta = f"acciones[{i}]"
    if not isinstance(a, dict):
        errores.append(f"{ruta}: debe ser un objeto")
        return
    nombre = a.get("nombre")
    if not isinstance(nombre, str) or not _NOMBRE_RE.match(nombre or ""):
        errores.append(f"{ruta}.nombre: falta o invalido (minusculas, digitos y guiones)")
    elif nombre in nombres:
        errores.append(f"{ruta}.nombre: '{nombre}' esta duplicado")
    else:
        nombres.add(nombre)
    desc = a.get("descripcion")
    if not isinstance(desc, str) or not desc.strip():
        errores.append(f"{ruta}.descripcion: falta o esta vacia")
    tipo = a.get("tipo")
    if tipo not in TIPOS_VALIDOS:
        errores.append(f"{ruta}.tipo: debe ser uno de {sorted(TIPOS_VALIDOS)}")
    if tipo in {"mover", "copiar"}:
        if not isinstance(a.get("destino"), str) or not a["destino"].strip():
            errores.append(f"{ruta}.destino: obligatorio para el tipo '{tipo}'")
    if tipo == "renombrar":
        if not isinstance(a.get("plantilla"), str) or not a["plantilla"].strip():
            errores.append(f"{ruta}.plantilla: obligatoria para el tipo 'renombrar'")
    if "confirmar" in a and not isinstance(a["confirmar"], bool):
        errores.append(f"{ruta}.confirmar: debe ser true o false")
    if "origen" in a and not isinstance(a["origen"], str):
        errores.append(f"{ruta}.origen: debe ser texto")
    if "filtro" in a:
        _validar_filtro(a["filtro"], ruta, errores)


def cargar_configuracion(ruta: Path) -> dict:
    """Lee y valida acciones.json. Lanza ConfigError con el detalle."""
    if not ruta.exists():
        raise ConfigError(f"No existe el fichero de configuracion: {ruta}")
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"No se puede leer {ruta}: {exc}")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"JSON invalido en {ruta}: {exc.msg} (linea {exc.lineno}, columna {exc.colno})")

    errores: list[str] = []
    if not isinstance(datos, dict):
        raise ConfigError("La raiz del JSON debe ser un objeto")
    if not isinstance(datos.get("version"), int):
        errores.append("'version': debe ser un entero")
    acciones = datos.get("acciones")
    if not isinstance(acciones, list):
        errores.append("'acciones': debe ser una lista")
    elif not acciones:
        errores.append("'acciones': la lista esta vacia")
    nombres: set[str] = set()
    if isinstance(acciones, list):
        for i, a in enumerate(acciones):
            _validar_accion(a, i, nombres, errores)
    if errores:
        raise ConfigError("Configuracion invalida:\n- " + "\n- ".join(errores))
    return datos