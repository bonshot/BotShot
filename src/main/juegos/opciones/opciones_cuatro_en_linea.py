"""
Módulo para las opciones del 4 en Línea.
"""

from .opciones_abc import OpcionesBase


class OpcionesCuatroEnLinea(OpcionesBase):
    """
    Opciones del 4 en Línea.
    """

    def __init__(self,
                 mensaje_inicial: str = "Viendo configuraciones del 4 en Línea") -> None:
        """
        Inicializa las opciones del 4 en Línea.
        """

        super().__init__(mensaje_inicial)

        self.modo_texto: bool = False
        self.primero_jugador_1: bool = True
        self.colores_default: bool = True


    def propiedades(self) -> list:
        """
        Devuelve una lista de las propiedades de esta clase
        de opciones, apta para procesarlas con un paginador.
        """

        return [self.modo_texto, self.primero_jugador_1, self.colores_default]


    def cambiar_orden_jugadores(self) -> bool:
        """
        Invierte el valor de la variable que decide si el
        primer jugador debería ir primero.

        Devuelve el nuevo valor.
        """

        self.primero_jugador_1 = not self.primero_jugador_1
        return self.primero_jugador_1


    def cambiar_modo_texto(self) -> bool:
        """
        Cambia entre si ver el juego como imagen o como una
        representación de caracteres.

        Devuelve el nuevo valor.
        """

        self.modo_texto = not self.modo_texto
        return self.modo_texto


    def usar_colores_default(self) -> bool:
        """
        Decide si usar colores predeterminados o no.
        """

        self.colores_default = not self.colores_default
        return self.colores_default
