"""IA conectada al motor: --simular no toca red; sin red no revienta."""

from pathlib import Path

from tareas.acciones import crear_accion
from tareas.motor import Motor


def _md(tmp_path):
    src = tmp_path / "s"
    src.mkdir()
    (src / "a.md").write_text("hola mundo " * 50, encoding="utf-8")
    return src


def test_ia_resumir_simular(tmp_path):
    src = _md(tmp_path)
    accion = crear_accion({"nombre": "r", "descripcion": "r", "tipo": "ia-resumir",
                           "origen": str(src), "filtro": {"extensiones": [".md"]}})
    res = Motor(accion, src).ejecutar(simular=True)
    assert res.total == 1
    assert not (src / "a.resumen.md").exists()


def test_ia_sin_red_no_revienta(tmp_path, monkeypatch):
    monkeypatch.delenv("CENTRO_IA_KEY", raising=False)
    monkeypatch.delenv("CENTRO_IA_URL", raising=False)
    src = _md(tmp_path)
    accion = crear_accion({"nombre": "r", "descripcion": "r", "tipo": "ia-resumir",
                           "origen": str(src), "filtro": {"extensiones": [".md"]}})
    res = Motor(accion, src).ejecutar(simular=False)
    assert res.total == 1
    assert res.realizados == 0
    assert res.omitidos == 1
    assert "error" in res.detalles[0]["estado"]