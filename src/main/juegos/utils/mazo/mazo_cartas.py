"""
Módulo que contiene un mazo de cartas.
"""

from collections import deque as Cola
from copy import deepcopy
from random import shuffle
from typing import Dict, Union, TypeAlias

from ..carta import Carta, Palo

StatsNaipes: TypeAlias = Dict[Union[int, str], int]


class _VisualizadorCartas:
    """
    Visualizador para usarse con context managers.
    """

    def __init__(self, mazo: "Mazo", cuantas_cartas: int, orden_inverso: bool=False) -> None:
        """
        Inicializa el visualizador.
        """

        self.mazo: "Mazo" = mazo
        self.n: int = cuantas_cartas
        self.inv: bool = orden_inverso
        self.cartas: list[Carta] = []


    def __enter__(self) -> None:
        """
        Desencola temporalmente del mazo.
        """

        for _ in range(self.n):
            if self.mazo.vacio():
                continue

            cart = self.mazo.get()
            if self.inv:
                self.cartas.insert(0, cart)
            else:
                self.cartas.append(cart)
        
        return self.cartas


    def __exit__(self, _exc_type, _exc_value, _exc_traceback) -> None:
        """
        Devuelve las cartas al mazo.
        """

        while self.cartas:
            cart = (self.cartas.pop(0)
                    if self.inv
                    else self.cartas.pop())
            self.mazo.put(cart, al_final=True)



class Mazo:
    """
    Mazo de cartas.
    """

    def __init__(self, entero: bool=True, ordenado: bool=False, vacio: bool=False) -> None:
        """
        Inicializa una instancia de 'Mazo'.

        'entero' da la opción de si generar el mazo con todas las
        50 cartas, o solo 40 (ignorando los 8, 9 y comodines).

        'ordenado' es si generarlo con las cartas en orden, o si ya
        generarlo mezclado.

        'vacio' ignora las otras opciones y devuelve un mazo vacío.
        """

        self._cola: Cola[Carta] = Cola()

        if vacio:
            return

        for palo in Palo:

            if palo == Palo.COMODIN:
                continue

            for i in range(1, 13):

                if not entero and i in (8, 9):
                    continue

                self._cola.append(Carta(num=i, palo=palo))

        if entero:
            for _ in range(2):
                self._cola.append(Carta(palo=Palo.COMODIN))

        if not ordenado:
            self.mezclar()


    def __len__(self) -> int:
        """
        Cuenta la cantidad de elementos en la cola.
        """

        return len(self.cola)


    @property
    def cola(self) -> Cola[Carta]:
        """
        Devuelve la cola de cartas.
        """

        return self._cola


    def put(self, carta: Carta, al_final: bool=False) -> None:
        """
        Encola una carta.

        'al_final' es una opción para usarlo como Pila también.
        """

        if al_final:
            self.cola.append(carta)
        else:
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

    def vaciar(self) -> None:
        """
        Vacía el mazo.
        """

        while not self.vacio():
            self.get()


    def mezclar(self, veces: int=5) -> None:
        """
        Mezcla el mazo.
        """

        for _ in range(veces):
            shuffle(self._cola)


    def copia(self) -> "Mazo":
        """
        Devuelve una copia profunda del Mazo.
        """

        return deepcopy(self)


    def contar_cartas(self) -> StatsNaipes:
        """
        Desencola un mazo entero y devuelve un diccionario con
        las estadísticas de este.
        """

        mazo = self.copia()
        stats: StatsNaipes = {}

        for key in list(range(1, 13)) + [palo.value for palo in Palo]:
            stats[key] = 0

        while not mazo.vacio():
            carta = mazo.get()
            stats[carta.palo.value] += 1
            if not carta.es_comodin():
                stats[carta.num] += 1

        return stats


    def ver_primeras(self, cuantas: int, /, *, inverso: bool=False) -> list[Carta]:
        """
        Devuelve una lista de cartas, y luego las devuelve al mazo.

        Se debe usar junto con `with`:
        """

        return _VisualizadorCartas(self, cuantas, inverso)
