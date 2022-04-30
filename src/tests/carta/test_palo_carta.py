"""
Módulo para tests de la clase Enum 'Palo'.
"""

from unittest import TestCase

from src.main.carta.palo_carta import *


class TestPalo(TestCase):
    """
    Tests de Palo de Naipes Españoles.
    """

    def test_1_tiene_solo_5_palos(self) -> None:
        """
        Sólo deberían estar los 4 palos y el comodín.
        """

        palos = list(Palo)

        self.assertEqual(len(palos), 5)


    def test_2_palos_tienen_nombres_correctos(self) -> None:
        """
        Los palos deberían ser:
        'Espada', 'Oro', 'Copa', 'Basto', 'Comodin'
        """

        palos = [palo.value for palo in Palo]
        lista_esperada = ['Espada', 'Oro', 'Copa', 'Basto', 'Comodin']

        self.assertEqual(palos, lista_esperada)