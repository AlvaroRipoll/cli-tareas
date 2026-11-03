# Changelog

Formato Keep a Changelog, versionado SemVer.

## [1.0.0] - 2026-11-02
### Anadido
- 3 acciones de sistema: ordenar-descargas, renombrar-fotos, limpiar-temporales.
- 2 acciones de IA: resumir-apuntes, renombrar-por-contenido (servidor del centro).
- Validacion estricta de acciones.json con codigo de salida 3.
- Opciones globales --config, --simular, --si, --json.
- Modo sin red: la CLI degrada con aviso y codigo 0, sin traceback.
- Pruebas pytest (16) y CI en Ubuntu/Windows/macOS.
### Corregido
- Modelo de IA sin prefijo de proveedor (403).
- Timeout de IA a 180s para resumenes largos.

## [0.1.0] - 2026-10-26
- Estructura inicial uv + Typer + Rich, comandos version y listar.
