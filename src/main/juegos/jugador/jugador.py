"""
Módulo para el modelado de un jugador.
"""

from typing import Optional, TypeAlias

LONGITUD_MAXIMA_NOMBRE = 30
"""
Longitud máxima que debe tener un nombre de jugador.
"""

ListaJugadores: TypeAlias = list["Jugador"]


class Jugador:
    """
    Clase que emula un jugador.
    """

    def __init__(self,
                 nombre: str,
                 id: str,
                 emoji_preferido: Optional[str]=None,
                 **kwargs) -> None:
        """
        Inicializa una instancia de 'Jugador'.

        'nombre' e 'id' son obligatorios, pues son lo que se usa para identificar al jugador.

        Los argumentos extra se guardan en un atributo especial 'extras'
        """

        self.nombre: str = (nombre
                            if len(nombre) <= LONGITUD_MAXIMA_NOMBRE
                            else nombre[:LONGITUD_MAXIMA_NOMBRE])
        self.id: str = id
        self.emoji: Optional[str] = emoji_preferido

        self.extras: dict = kwargs


    def cambiar_nombre(self, nuevo_nombre: str) -> bool:
        """
        Intenta cambiar el nombre del jugador.

        Si tiene éxito, devuelve `True`, o sino devuelve `False`.
        """

        if (not isinstance(nuevo_nombre, str)
            or len(nuevo_nombre) > LONGITUD_MAXIMA_NOMBRE):
            return False

        self.nombre = nuevo_nombre
        return True


    def __eq__(self, otro: "Jugador") -> bool:
        """
        Determina si dos jugadores son iguales.
        """

        return self.id == otro.id and self.nombre == otro.nombre
