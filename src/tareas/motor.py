"""Motor: calcula el plan y lo ejecuta, separado de la interfaz."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tareas.acciones import Accion


@dataclass
class Resultado:
    accion: str
    tipo: str
    simulacion: bool
    total: int = 0
    realizados: int = 0
    omitidos: int = 0
    detalles: list = field(default_factory=list)


class Motor:
    def __init__(self, accion: Accion, carpeta: Path):
        self.accion = accion
        self.carpeta = carpeta

    def plan(self):
        ficheros = self.accion.ficheros_afectados(self.carpeta)
        plan = []
        for n, p in enumerate(ficheros, start=1):
            dst = self.accion.destino_para(p, n)
            colision = self.accion.tipo in {"mover", "copiar"} and dst is not None and dst.exists()
            plan.append((p, dst, colision))
        return plan

    def ejecutar(self, simular: bool) -> Resultado:
        plan = self.plan()
        res = Resultado(accion=self.accion.nombre, tipo=self.accion.tipo,
                        simulacion=simular, total=len(plan))
        for src, dst, omitido in plan:
            if omitido:
                res.omitidos += 1
                res.detalles.append({"origen": str(src), "destino": str(dst),
                                     "estado": "omitido (ya existe)"})
                continue
            try:
                self.accion.operar(src, dst, simular)
            except OSError as exc:
                res.omitidos += 1
                res.detalles.append({"origen": str(src), "destino": str(dst),
                                     "estado": f"error: {exc}"})
                continue
            res.realizados += 1
            res.detalles.append({"origen": str(src),
                                 "destino": str(dst) if dst else None,
                                 "estado": "simulado" if simular else "hecho"})
        return res