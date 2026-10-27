"""Motor de ejecucion de acciones, separado de la interfaz (Semana 2)."""


class Motor:
    """Ejecuta una Accion sobre una carpeta. Pendiente (Semana 2)."""

    def __init__(self, accion=None, carpeta=None):
        self.accion = accion
        self.carpeta = carpeta

    def ejecutar(self, simular: bool = False):
        raise NotImplementedError("El motor llega en la Semana 2.")
