"""
Módulo para las opciones del Tres en Raya.
"""

from .opciones_abc import OpcionesBase


class OpcionesTaTeTi(OpcionesBase):
    """
    Opciones del Tres en Raya.
    """

    def __init__(self,
                 mensaje_inicial: str = "Viendo configuraciones del Tres en Raya") -> None:
        """
        Inicializa las opciones del Tres en Raya.
        """

        super().__init__(mensaje_inicial)

        self.empieza_primer_jugador: bool = True


    def propiedades(self) -> list:
        """
        Devuelve una lista de las propiedades de esta clase
        de opciones, apta para procesarlas con un paginador.
        """

        return [self.empieza_primer_jugador]


    def cambiar_orden_jugadores(self) -> bool:
        """
        Invierte el valor de la variable que decide si el
        primer jugador debería ir primero.
        Devuelve el nuevo valor.
        """

        self.empieza_primer_jugador = not self.empieza_primer_jugador
        return self.empieza_primer_jugador
