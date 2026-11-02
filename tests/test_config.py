"""Pruebas de validacion de acciones.json."""

from pathlib import Path

import pytest

from tareas.config import cargar_configuracion
from tareas.errores import ConfigError


def _escribir(tmp_path: Path, texto: str) -> Path:
    ruta = tmp_path / "acciones.json"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


VALIDA = """{
  "version": 1,
  "acciones": [
    {"nombre": "ordenar", "descripcion": "Mueve docs", "tipo": "mover",
     "origen": "~/Baixades", "destino": "~/Documents/Ordenados",
     "filtro": {"extensiones": [".pdf"]}},
    {"nombre": "limpiar", "descripcion": "Borra temporales", "tipo": "borrar",
     "origen": "~/Proyectos", "filtro": {"patron": "\\\\.tmp$"}, "confirmar": true}
  ]
}"""


def test_config_valida(tmp_path):
    ruta = _escribir(tmp_path, VALIDA)
    datos = cargar_configuracion(ruta)
    assert datos["version"] == 1
    assert len(datos["acciones"]) == 2
    assert datos["acciones"][0]["nombre"] == "ordenar"


def test_fichero_no_existe(tmp_path):
    with pytest.raises(ConfigError) as exc:
        cargar_configuracion(tmp_path / "no-existe.json")
    assert "No existe" in str(exc.value)


def test_json_roto(tmp_path):
    ruta = _escribir(tmp_path, "{ esto no es json valido")
    with pytest.raises(ConfigError) as exc:
        cargar_configuracion(ruta)
    assert "JSON invalido" in str(exc.value)


def test_falta_version(tmp_path):
    ruta = _escribir(tmp_path, '{"acciones": [{"nombre": "a", "descripcion": "x", "tipo": "mover", "destino": "/tmp"}]}')
    with pytest.raises(ConfigError) as exc:
        cargar_configuracion(ruta)
    assert "version" in str(exc.value)


def test_nombre_invalido(tmp_path):
    ruta = _escribir(tmp_path, '{"version": 1, "acciones": [{"nombre": "Sin-Guiones", "descripcion": "x", "tipo": "mover", "destino": "/tmp"}]}')
    with pytest.raises(ConfigError) as exc:
        cargar_configuracion(ruta)
    assert "nombre" in str(exc.value)


def test_duplicado(tmp_path):
    ruta = _escribir(tmp_path, '{"version": 1, "acciones": [{"nombre": "a", "descripcion": "x", "tipo": "mover", "destino": "/tmp"}, {"nombre": "a", "descripcion": "y", "tipo": "mover", "destino": "/tmp"}]}')
    with pytest.raises(ConfigError) as exc:
        cargar_configuracion(ruta)
    assert "duplicado" in str(exc.value)