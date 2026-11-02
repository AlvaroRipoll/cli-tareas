"""Pruebas del motor: mover, renombrar, borrar, simulacion y casos feos."""

from pathlib import Path

from tareas.acciones import crear_accion
from tareas.motor import Motor


def _tocar(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x", encoding="utf-8")
    return p


def test_mover_real(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    _tocar(src / "a.pdf")
    _tocar(src / "b.txt")
    accion = crear_accion({"nombre": "m", "descripcion": "mover", "tipo": "mover",
                           "origen": str(src), "destino": str(dst),
                           "filtro": {"extensiones": [".pdf"]}})
    Motor(accion, src).ejecutar(simular=False)
    assert (dst / "a.pdf").exists()
    assert not (src / "a.pdf").exists()
    assert (src / "b.txt").exists()


def test_simular_no_toca(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    _tocar(src / "a.pdf")
    accion = crear_accion({"nombre": "m", "descripcion": "mover", "tipo": "mover",
                           "origen": str(src), "destino": str(dst),
                           "filtro": {"extensiones": [".pdf"]}})
    Motor(accion, src).ejecutar(simular=True)
    assert (src / "a.pdf").exists()
    assert not (dst / "a.pdf").exists()


def test_renombrar_real(tmp_path):
    src = tmp_path / "src"
    _tocar(src / "foto.jpg")
    accion = crear_accion({"nombre": "r", "descripcion": "renombrar", "tipo": "renombrar",
                           "origen": str(src), "filtro": {"extensiones": [".jpg"]},
                           "plantilla": "{fecha:%Y-%m-%d}_{n:03}{ext}"})
    Motor(accion, src).ejecutar(simular=False)
    jpgs = list(src.glob("*.jpg"))
    assert len(jpgs) == 1
    assert jpgs[0].name.endswith("_001.jpg")
    assert "foto" not in jpgs[0].name.lower()


def test_borrar_real(tmp_path):
    src = tmp_path / "src"
    _tocar(src / "x.tmp")
    _tocar(src / "y.txt")
    accion = crear_accion({"nombre": "b", "descripcion": "borrar", "tipo": "borrar",
                           "origen": str(src), "filtro": {"patron": "\\.(tmp|bak)$"}})
    Motor(accion, src).ejecutar(simular=False)
    assert not (src / "x.tmp").exists()
    assert (src / "y.txt").exists()


def test_colision_se_omite(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    _tocar(src / "a.pdf")
    _tocar(dst / "a.pdf")
    accion = crear_accion({"nombre": "m", "descripcion": "mover", "tipo": "mover",
                           "origen": str(src), "destino": str(dst),
                           "filtro": {"extensiones": [".pdf"]}})
    res = Motor(accion, src).ejecutar(simular=False)
    assert res.omitidos == 1
    assert (src / "a.pdf").exists()


def test_carpeta_inexistente(tmp_path):
    accion = crear_accion({"nombre": "m", "descripcion": "mover", "tipo": "mover",
                           "origen": str(tmp_path / "nope"), "destino": str(tmp_path / "d"),
                           "filtro": {"extensiones": [".pdf"]}})
    res = Motor(accion, tmp_path / "nope").ejecutar(simular=False)
    assert res.total == 0
    assert res.realizados == 0