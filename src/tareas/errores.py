"""Excepciones propias de tareas."""


class TareasError(Exception):
    """Error base de la aplicacion."""


class ConfigError(TareasError):
    """Error al leer o validar la configuracion."""


class AccionNoValida(TareasError):
    """La accion pedida no existe o no es valida."""


class IaError(TareasError):
    """La IA no esta disponible (sin red, sin clave o fallo del servidor)."""