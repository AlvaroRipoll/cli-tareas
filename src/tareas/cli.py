"""Interfaz de linea de ordenes (Typer) para tareas."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tareas import __version__
from tareas.config import cargar_configuracion
from tareas.errores import ConfigError

app = typer.Typer(
    name="tareas",
    help="CLI para ordenar, limpiar y resumir archivos mediante acciones en acciones.json.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", help="Ruta a un acciones.json alternativo."),
) -> None:
    ctx.obj = {"config": config}


def _ruta_config(ctx: typer.Context) -> Path:
    obj = getattr(ctx, "obj", None) or {}
    return obj.get("config") or Path("acciones.json")


@app.command()
def version() -> None:
    """Muestra la version instalada."""
    console.print(f"tareas {__version__}")


def _tipo(ruta: Path) -> str:
    if ruta.is_dir():
        return "dir"
    sufijo = ruta.suffix.lower()
    return sufijo if sufijo else "file"


def _tamano(ruta: Path) -> str:
    if ruta.is_dir():
        return "-"
    try:
        n = float(ruta.stat().st_size)
    except OSError:
        return "?"
    for unidad in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidad == "GB":
            return f"{n:.0f}{unidad}" if unidad == "B" else f"{n:.1f}{unidad}"
        n /= 1024
    return f"{n:.1f}GB"


def _fecha(ruta: Path) -> str:
    try:
        return datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return "?"


@app.command()
def listar(
    carpeta: Optional[Path] = typer.Argument(None, help="Carpeta a listar (por defecto, la actual)."),
    json_salida: bool = typer.Option(False, "--json", help="Salida en JSON para maquinas."),
) -> None:
    """Lista los ficheros de una carpeta con tipo, tamano y fecha."""
    ruta = (carpeta or Path.cwd()).expanduser()
    if not ruta.exists():
        console.print(f"[red]Error:[/red] la carpeta no existe: {ruta}")
        raise typer.Exit(code=1)
    if not ruta.is_dir():
        console.print(f"[red]Error:[/red] no es una carpeta: {ruta}")
        raise typer.Exit(code=1)
    entradas = sorted(ruta.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    if json_salida:
        datos = [
            {"nombre": p.name, "tipo": _tipo(p), "tamano": _tamano(p), "fecha": _fecha(p)}
            for p in entradas
        ]
        print(json.dumps(datos, ensure_ascii=False, indent=2))
        return
    tabla = Table(title=f"Contenido de {ruta}")
    tabla.add_column("Nombre", style="cyan")
    tabla.add_column("Tipo", style="magenta")
    tabla.add_column("Tamano", justify="right")
    tabla.add_column("Fecha", style="dim")
    for p in entradas:
        tabla.add_row(p.name, _tipo(p), _tamano(p), _fecha(p))
    console.print(tabla)


@app.command()
def validar(ctx: typer.Context) -> None:
    """Comprueba acciones.json y dice exactamente que campo falla."""
    ruta = _ruta_config(ctx)
    try:
        datos = cargar_configuracion(ruta)
    except ConfigError as exc:
        console.print(f"[red]Configuracion invalida:[/red]\n{exc}")
        raise typer.Exit(code=3)
    console.print(f"[green]OK:[/green] {ruta} es valida. {len(datos['acciones'])} acciones definidas.")


@app.command()
def acciones(
    ctx: typer.Context,
    json_salida: bool = typer.Option(False, "--json", help="Salida en JSON para maquinas."),
) -> None:
    """Lista las acciones definidas en acciones.json."""
    ruta = _ruta_config(ctx)
    try:
        datos = cargar_configuracion(ruta)
    except ConfigError as exc:
        console.print(f"[red]Configuracion invalida:[/red]\n{exc}")
        raise typer.Exit(code=3)
    if json_salida:
        print(json.dumps(datos["acciones"], ensure_ascii=False, indent=2))
        return
    tabla = Table(title=f"Acciones en {ruta}")
    tabla.add_column("Nombre", style="cyan")
    tabla.add_column("Tipo", style="magenta")
    tabla.add_column("Descripcion")
    for a in datos["acciones"]:
        tabla.add_row(a["nombre"], a["tipo"], a["descripcion"])
    console.print(tabla)