"""
Módulo para tests de la clase 'Carta'.
"""

from unittest import TestCase

from src.main.juegos.utils.carta.naipe_espaniol import *


class TestCarta(TestCase):
    """
    Tests de Naipes Españoles.
    """

    def test_1_numero_invalido_rompe(self) -> None:
        """
        Debería ser un número entre 1 y 12.
        """

        with self.assertRaises(TypeError):
            Carta(num=23.0)

        with self.assertRaises(ValueError):
            Carta(num=23)


    def test_2_palo_invalido_rompe(self) -> None:
        """
        Debería provenir del Enum 'Palo'.
        """

        with self.assertRaises(TypeError):
            Carta(palo=1)

        with self.assertRaises(TypeError):
            Carta(palo="palo_invalido")

        with self.assertRaises(TypeError):
            Carta(palo=Palo)


    def test_3_comodin_posee_numero_mayor_a_12(self) -> None:
        """
        El comodín, por defecto, le gana a cualquier otra carta
        en términos de números.
        """

        carta_1 = Carta(num=1, palo=Palo.ORO)
        carta_2 = Carta(palo=Palo.COMODIN)

        self.assertGreater(carta_2.num, 12)

        # estos dos deberían ser lo mismo
        self.assertGreater(carta_2.num, carta_1.num)
        self.assertGreater(carta_2, carta_1)


    def test_4_cartas_son_iguales_si_tienen_mismo_numero_y_palo(self) -> None:
        """
        Dos cartas son consideradas equivalentes (x == y) si tienen el mismo
        número y el mismo palo.
        """

        carta_1 = Carta(num=10, palo=Palo.BASTO)
        carta_2 = Carta(num=10, palo=Palo.ORO)
        carta_3 = Carta(num=5, palo=Palo.ORO)
        carta_4 = Carta(num=10, palo=Palo.BASTO)

        self.assertNotEqual(carta_1, carta_2)
        self.assertNotEqual(carta_1, carta_3)
        self.assertNotEqual(carta_2, carta_3)
        self.assertEqual(carta_1, carta_4)



    def test_5_comodin_ignora_numero(self) -> None:
        """
        Si, en el constructor de una carta, se especifican
        tanto un número como el palo de comodín, el número
        debería ser ignorado, pues el comodín tiene un valor constante.
        """

        numero_cualquiera = 11

        carta_1 = Carta(palo=Palo.COMODIN)
        carta_2 = Carta(num=numero_cualquiera, palo=Palo.COMODIN)

        self.assertNotEqual(carta_2.num, numero_cualquiera)
        self.assertEqual(carta_1.num, carta_2.num)
        self.assertEqual(carta_1, carta_2)