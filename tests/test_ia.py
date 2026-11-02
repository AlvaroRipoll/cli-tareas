"""El modo sin red no revienta: sin credenciales, IaError con mensaje claro."""

import pytest

from tareas import ia
from tareas.errores import IaError


def test_sin_clave_modo_sin_red(monkeypatch):
    monkeypatch.delenv("CENTRO_IA_KEY", raising=False)
    monkeypatch.setenv("CENTRO_IA_URL", "https://ia.simarro/llmapi/v1")
    assert ia.disponible() is False
    with pytest.raises(IaError):
        ia.completar("hola")


def test_sin_url_modo_sin_red(monkeypatch):
    monkeypatch.delenv("CENTRO_IA_URL", raising=False)
    monkeypatch.setenv("CENTRO_IA_KEY", "x")
    assert ia.disponible() is False
    with pytest.raises(IaError):
        ia.completar("hola")