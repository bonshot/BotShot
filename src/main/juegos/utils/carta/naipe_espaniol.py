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

        # Temporalmente hasta que se asignen bien más abajo
        self._num: Optional[int] = num
        self._palo: Optional[Palo] = palo

        self.num: int = num
        self.palo: Palo = palo


    def __str__(self) -> str:
        """
        Representa la carta en forma de string.
        """

        if self.palo == Palo.COMODIN:
            return "Carta Comodín"

        return f"Carta {self.num} de {self.palo.value}"


    def __repr__(self) -> str:
        """
        Devuelve la representación de la carta.
        """

        return f"<{str(self)}>"


    @property
    def num(self) -> int:
        """
        Devuelve el número de la carta.
        """

        return self._num


    @num.setter
    def num(self, nuevo_num: Optional[int]=None) -> None:
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

        return (self.es_comodin() or
                otra.es_comodin() or
                self.mismo_num(otra) or
                self.mismo_palo(otra))


    def es_anterior_a(self, otra: "Carta") -> bool:
        """
        Verifica si el número de una carta es justo uno anterior
        al de otra. Si la otra es un 1 (uno), esto es falso.
        """

        return (self.num == (otra.num - 1)
                if otra.num != 1
                else False)


    def es_posterior_a(self, otra: "Carta") -> bool:
        """
        Verifica si el número de una carta es justo uno posterior
        al de otra. Si la otra es un 12 (doce), esto es falso.
        """

        return (self.num == (otra.num + 1)
                if otra.num != 12
                else False)


    def hace_escalera_a(self, otra: "Carta") -> bool:
        """
        Verifica si una carta tiene potencial de hacerle escalera a otra.
        """

        return (self.mismo_palo(otra) and
                (self.es_anterior_a(otra) or self.es_posterior_a(otra)))


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
