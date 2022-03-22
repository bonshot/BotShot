"""
Módulo que contiene un mazo de cartas.
"""

from queue import SimpleQueue as Cola
from random import shuffle

from .naipe_espaniol import Carta
from .palo_carta import Palo


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
            self._cola.put(temp_list.pop())


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

        self.cola.put(carta)


    def get(self) -> Carta:
        """
        Desencola una carta.
        """

        return self.cola.get()


    def vacio(self) -> bool:
        """
        Verifica si el mazo está vacía.
        """

        return self.cola.empty()
