# ADR 0001: Configuracion externa en acciones.json

- Estado: Aceptado
- Fecha: 2026-11-02

## Contexto

La CLI debe ejecutar acciones sobre ficheros (mover, renombrar, borrar, copiar y acciones
de IA). Si cada accion se programara dentro del codigo, anadir o cambiar una accion
exigiria modificar y reinstalar el programa, y solo un desarrollador podria ampliarla.

## Decision

Las acciones se describen en un fichero externo, `acciones.json`, y el motor las
interpreta. El codigo define los tipos de accion (mover, renombrar, borrar, copiar,
ia-resumir, ia-renombrar) como clases, pero las instancias concretas (carpeta, filtro,
destino) viven en el JSON.

## Consecuencias

- Positivo: anadir una accion nueva no exige tocar el codigo; el usuario amplia la
  herramienta editando el JSON.
- Positivo: la configuracion es portable entre sistemas y facil de versionar.
- Negativo: hace falta una capa de validacion estricta (config.py) que detecte JSON mal
  formado o campos faltantes y lo reporte con mensajes claros y codigo de salida 3.
- Mitigacion: `tareas validar` comprueba el JSON antes de ejecutar nada.
