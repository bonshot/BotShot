"""
Módulo que contiene una carta de tipo de naipes españoles.
"""

from math import inf
from random import randint
from secrets import choice
from typing import Optional

from .palo_carta import Palo


class Carta:
    """
    Naipe español.
    """

    def __init__(self, *, num: Optional[int]=None, palo: Optional[Palo]=None) -> None:
        """
        Inicializa una instancia de 'Carta'.
        """

        self._num: int = num
        self._palo: Palo = palo


    def __str__(self) -> str:
        """
        Representa la carta en forma de string.
        """

        if self.palo == Palo.COMODIN:
            return "Carta Comodín"

        return f"Carta {self.num} de {self.palo.value}"


    @property
    def num(self) -> int:
        """
        Devuelve el número de la carta.
        """

        return self._num


    @num.setter
    def num(self, nuevo_num: Optional[int]) -> None:
        """
        Asigna un nuevo valor al numero de la carta.
        """

        if not isinstance(nuevo_num, Optional[int]):
            raise TypeError("El número especificado no es un entero.")

        if nuevo_num and (nuevo_num < 1 or nuevo_num > 12):
            raise ValueError(f"Número {nuevo_num} no válido. Debe ser un entero entre 1 y 12.")

        if self.palo == Palo.COMODIN:
            nuevo_num = inf
        elif not nuevo_num:
            nuevo_num = randint(1, 12)

        self._num: int = nuevo_num


    @property
    def palo(self) -> Palo:
        """
        Devuelve el palo de la carta.
        """

        return self._palo


    @palo.setter
    def palo(self, nuevo_palo: Optional[Palo]) -> None:
        """
        Asigna un nuevo valor al palo de la carta.
        """

        if not isinstance(nuevo_palo, Optional[Palo]):
            raise TypeError("Palo especificado no válido.")

        if not nuevo_palo:
            nuevo_palo = choice(list(Palo))

        self._palo = nuevo_palo


    def mismo_num(self, otra: "Carta") -> bool:
        """
        Verifica si una carta tiene el mismo número que otra.
        """

        return self.num == otra.num


    def mismo_palo(self, otra: "Carta") -> bool:
        """
        Verifica si una carta tiene el mismo palo que otra.
        """

        return self.palo == otra.palo


    def es_comodin(self) -> bool:
        """
        Verifica si esta carta es un comodin.
        """

        return self.palo == Palo.COMODIN


    def compatible(self, otra: "Carta") -> bool:
        """
        Verifica si una carta tiene el mismo número o palo que otra.
        Los comodines son automáticamente compatibles con cualquier otra carta.
        """

        return any((self.es_comodin(), otra.es_comodin(),
                    self.mismo_num(otra), self.mismo_palo(otra)))


    def __eq__(self, otra: "Carta") -> bool:
        """
        Verifica si una carta tiene el mismo número y palo que otra.
        """

        return self.mismo_num(otra) and self.mismo_palo(otra)


    def __gt__(self, otra: "Carta") -> bool:
        """
        Verifica si el numero de una carta es mayor que el de otra.
        """

        return self.num > otra.num


    def __ge__(self, otra: "Carta") -> bool:
        """
        Verifica si el numero de una carta es mayor o igual que el de otra.
        """

        return self.num >= otra.num


    def __lt__(self, otra: "Carta") -> bool:
        """
        Verifica si el numero de una carta es menor que el de otra.
        """

        return self.num < otra.num


    def __le__(self, otra: "Carta") -> bool:
        """
        Verifica si el numero de una carta es menor o igual que el de otra.
        """

        return self.num <= otra.num
