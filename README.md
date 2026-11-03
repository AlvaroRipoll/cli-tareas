# tareas

CLI para ordenar, limpiar y resumir archivos mediante acciones definidas en `acciones.json`.
Combina lo que hace el sistema operativo (mover, renombrar, borrar, copiar) con la IA del
centro (resumir, renombrar por contenido). Funciona en Linux, Windows y macOS.

## Requisitos

- [uv](https://docs.astral.sh/uv/). uv instala Python 3.12 y las dependencias.

## Instalacion

Como comando global desde GitHub:

    uv tool install git+https://github.com/AlvaroRipoll/cli-tareas

O en modo editable (desarrollo):

    git clone git@github.com:AlvaroRipoll/cli-tareas.git
    cd cli-tareas
    uv tool install --editable .

Desinstalar: `uv tool uninstall tareas`.

## Uso

    tareas --help
    tareas version
    tareas listar [CARPETA] [--json]
    tareas acciones [--json]
    tareas validar
    tareas ejecutar NOMBRE [CARPETA] [--simular] [--si] [--json]
    tareas --config RUTA ...

- `--simular`: muestra que haria sin tocar nada. Usar SIEMPRE antes de ejecutar.
- `--si`: no pregunta antes de acciones destructivas (para scripts).
- `--config`: usa otro `acciones.json`.
- `--json`: salida para maquinas.

## Codigo de salida

| Codigo | Significado |
|---|---|
| 0 | Correcto (incl. nada que hacer o degradacion sin red) |
| 1 | Fallo al ejecutar la accion |
| 2 | Error de uso (accion inexistente) |
| 3 | Configuracion invalida |

## acciones.json

Las acciones NO estan en el codigo: se describen en `acciones.json`. Anadir una accion no
exige tocar el codigo (ver `docs/adr/0001-configuracion-externa.md`).

    {
      "version": 1,
      "acciones": [
        { "nombre": "ordenar-descargas", "descripcion": "...", "tipo": "mover",
          "origen": "~/Baixades", "filtro": { "extensiones": [".pdf", ".docx"] },
          "destino": "~/Documents/Ordenados" }
      ]
    }

Campos: `version`, `acciones[]` con `nombre`, `descripcion`, `tipo`
(`mover|copiar|renombrar|borrar|ia-resumir|ia-renombrar`), `origen`, `destino`, `filtro`
(`extensiones`, `patron`, `mas_antiguo_que_dias`), `plantilla`, `confirmar`.

## Capa IA

`ia-resumir` y `ia-renombrar` llaman al servidor de IA del centro (openai-compatible). La
clave se lee de variables de entorno (`CENTRO_IA_URL`, `CENTRO_IA_KEY`), nunca esta en el
repo. Ver `.env.example`.

- Modo sin red: si faltan credenciales o el servidor no responde (fuera de la red del
  instituto), la CLI no revienta: lo avisa en la tabla y termina con codigo 0.
- Limitacion honesta: la IA lee texto plano (`.md`, `.txt`). No parsea PDFs (eso exigiria
  `pypdf`). Para resumir un PDF, pasalo antes a texto con `pandoc`.

## Multiplataforma

Rutas con `pathlib`, `~` con `expanduser()`, UTF-8 explicito, sin `shell=True`, saltos de
linea normalizados con `.gitattributes`, colores con Rich. Probado en CI (Ubuntu, Windows,
macOS) en cada push.

## Seguridad

- Ninguna clave en el repo ni en su historial (minimo de entrega).
- Acciones destructivas: `--simular` primero y confirmacion salvo `--si`.
- Probar en `~/pruebas-tareas`, nunca en ficheros reales hasta validar.

## Desarrollo

    uv sync
    uv run tareas --help
    uv run pytest -v

CI: `.github/workflows/ci.yml` ejecuta las pruebas en los tres sistemas en cada push.
