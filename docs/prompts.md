# Prompts clave del desarrollo

Registro de prompts usados para implementar y auditar (metodo del curso).

- Crea una CLI con Typer con comandos version y listar usando pathlib y Rich.
- Anade validacion de acciones.json en config.py con errores propios y codigo 3.
- Implementa el motor separado de la interfaz: plan() y ejecutar(simular).
- Cada tipo de accion es una clase registrada por tipo (mover, renombrar, borrar, ia-*).
- Proveedor de IA con urllib, sin dependencias, con modo sin red (IaError controlado).
- Fix: el modelo de IA va sin prefijo de proveedor (403 key_model_access_denied).
- Fix: sube timeout de IA a 180s para resumenes largos.

Lo que no se sabe explicar, no se entrega: cada prompt tiene su commit correspondiente.
