"""
Módulo que contiene un mazo de cartas.
"""

from collections import deque as Cola
from copy import deepcopy
from random import shuffle
from typing import Dict, Union, TypeAlias

from ..carta import Carta, Palo

StatsNaipes: TypeAlias = Dict[Union[int, str], int]


class Mazo:
    """
    Mazo de cartas.
    """

    def __init__(self, entero: bool=True) -> None:
        """
        Inicializa una instancia de 'Mazo'.

        'entero' da la opción de si generar el mazo con todas las
        50 cartas, o solo 40 (ignorando los 8, 9 y comodines).
        """

        self._cola: Cola[Carta] = Cola()
        temp_list: list = []

        for palo in Palo:

            if palo == Palo.COMODIN:
                continue

            for i in range(1, 13):

                if not entero and i in (8, 9):
                    continue

                temp_list.append(Carta(num=i, palo=palo))

        if entero:
            for _ in range(2):
                temp_list.append(Carta(palo=Palo.COMODIN))

        shuffle(temp_list)
        while temp_list:
            self.cola.appendleft(temp_list.pop())


    @property
    def cola(self) -> Cola[Carta]:
        """
        Devuelve la cola de cartas.
        """

        return self._cola


    def put(self, carta: Carta) -> None:
        """
        Encola una carta.
        """

        self.cola.appendleft(carta)


    def get(self) -> Carta:
        """
        Desencola una carta.
        """

        return self.cola.pop()


    def vacio(self) -> bool:
        """
        Verifica si el mazo está vacía.
        """

        return not self.cola


    def __len__(self) -> int:
        """
        Cuenta la cantidad de elementos en la cola.
        """

        return len(self.cola)


    def contar_cartas(self) -> StatsNaipes:
        """
        Desencola un mazo entero y devuelve un diccionario con
        las estadísticas de este.
        """

        mazo = deepcopy(self)
        stats: StatsNaipes = {}

        for key in list(range(1, 13)) + [palo.value for palo in Palo]:
            stats[key] = 0

        while not mazo.vacio():
            carta = mazo.get()
            stats[carta.palo.value] += 1
            if not carta.es_comodin():
                stats[carta.num] += 1

        return stats
