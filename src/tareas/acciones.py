"""Clases de acciones: cada tipo es una clase, elegida por 'tipo' desde acciones.json."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from tareas import ia
from tareas.errores import AccionNoValida


@dataclass
class Accion:
    nombre: str
    descripcion: str
    tipo: str
    origen: Optional[str] = None
    destino: Optional[str] = None
    filtro: Optional[dict] = None
    plantilla: Optional[str] = None
    confirmar: bool = False

    def __post_init__(self):
        if self.filtro is None:
            self.filtro = {}

    @classmethod
    def from_dict(cls, d: dict) -> "Accion":
        return cls(
            nombre=d["nombre"],
            descripcion=d.get("descripcion", ""),
            tipo=d["tipo"],
            origen=d.get("origen"),
            destino=d.get("destino"),
            filtro=d.get("filtro") or {},
            plantilla=d.get("plantilla"),
            confirmar=bool(d.get("confirmar", False)),
        )

    def ficheros_afectados(self, carpeta: Path) -> list[Path]:
        if not carpeta.is_dir():
            return []
        exts = self.filtro.get("extensiones")
        patron = self.filtro.get("patron")
        dias = self.filtro.get("mas_antiguo_que_dias")
        rx = re.compile(patron) if patron else None
        umbral = None
        if isinstance(dias, int):
            umbral = datetime.now().timestamp() - dias * 86400
        res: list[Path] = []
        for p in sorted(carpeta.iterdir()):
            if not p.is_file():
                continue
            if exts and p.suffix.lower() not in [e.lower() for e in exts]:
                continue
            if rx and not rx.search(p.name):
                continue
            if umbral is not None:
                try:
                    if p.stat().st_mtime > umbral:
                        continue
                except OSError:
                    continue
            res.append(p)
        return res

    def nuevo_nombre(self, p: Path, n: int) -> str:
        if not self.plantilla:
            return p.name
        try:
            ext = p.suffix
            fecha = datetime.fromtimestamp(p.stat().st_mtime)
            return self.plantilla.format(fecha=fecha, n=n, ext=ext)
        except (KeyError, ValueError, OSError):
            return p.name

    def destino_para(self, p: Path, n: int) -> Optional[Path]:
        return None

    def operar(self, src: Path, dst: Optional[Path], simular: bool) -> None:
        raise NotImplementedError


class Mover(Accion):
    def destino_para(self, p, n):
        return Path(self.destino).expanduser() / p.name

    def operar(self, src, dst, simular):
        if simular or dst is None:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


class Copiar(Accion):
    def destino_para(self, p, n):
        return Path(self.destino).expanduser() / p.name

    def operar(self, src, dst, simular):
        if simular or dst is None:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))


class Renombrar(Accion):
    def destino_para(self, p, n):
        base = Path(self.origen).expanduser() if self.origen else p.parent
        return base / self.nuevo_nombre(p, n)

    def operar(self, src, dst, simular):
        if simular or dst is None:
            return
        src.rename(dst)


class Borrar(Accion):
    def destino_para(self, p, n):
        return None

    def operar(self, src, dst, simular):
        if simular:
            return
        src.unlink()


class IaResumir(Accion):
    def destino_para(self, p, n):
        return p.parent / (p.stem + ".resumen.md")

    def operar(self, src, dst, simular):
        if simular or dst is None:
            return
        texto = src.read_text(encoding="utf-8", errors="replace")
        dst.write_text(ia.resumir(texto) + "\n", encoding="utf-8")


class IaRenombrar(Accion):
    def destino_para(self, p, n):
        return p

    def operar(self, src, dst, simular):
        if simular:
            return
        texto = src.read_text(encoding="utf-8", errors="replace")
        nuevo = ia.nombre_sugerido(texto).strip().strip("\"'").replace(" ", "-").lower()
        if not nuevo:
            return
        src.rename(src.with_name(nuevo + src.suffix))


REGISTRO = {
    "mover": Mover,
    "copiar": Copiar,
    "renombrar": Renombrar,
    "borrar": Borrar,
    "ia-resumir": IaResumir,
    "ia-renombrar": IaRenombrar,
}


def crear_accion(d: dict) -> Accion:
    clase = REGISTRO.get(d.get("tipo"))
    if clase is None:
        raise AccionNoValida(f"Tipo de accion desconocido: {d.get('tipo')!r}")
    return clase.from_dict(d)