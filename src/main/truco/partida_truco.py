"""
Módulo que contiene la lógica de una partida de Truco.
"""

from time import time

class PartidaTruco:
    """
    Clase para albergar la lógica de una partida de Truco.
    """

    def __init__(self, nombre_creador: str="Anon") -> None:
        """
        Inicializa una instancia de 'PartidaTruco'.
        """

        self._id_partida: str = f"{''.join(str(time()).split('.'))}-{nombre_creador}"


    @property
    def id(self) -> str: # pylint: disable=invalid-name
        """
        Devuelve el id de esta partida.
        """

        return self._id_partida
