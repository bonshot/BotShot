"""
Módulo para tests de la clase 'Mazo'.
"""

from unittest import TestCase

from src.main.juegos.utils.mazo.mazo_cartas import *


class TestMazo(TestCase):
    """
    Tests para un mazo de Naipes Españoles.
    """

    def test_1_crea_mazos_enteros(self) -> None:
        """
        Un mazo 'entero' debería tener 50 cartas:
            - cartas del 1 al 12 por cada uno de los 4 palos normales
            - 2 cartas 'comodines'
        """

        mazo = Mazo(True)
        stats = mazo.contar_cartas()

        self.assertFalse(mazo.vacio())
        self.assertEqual(len(mazo), 50)

        for i in range(1, 13):
            self.assertEquals(stats[i], 4)

        for palo in Palo:
            if palo == Palo.COMODIN:
                numero_esperado = 2
            else:
                numero_esperado = 12
            self.assertEqual(stats[palo.value], numero_esperado)


    def test_2_crea_mazos_incompletos(self) -> None:
        """
        Un mazo 'no entero' debería contar con 40 cartas, en el que es
        similar al mazo 'entero', excepto que carece de los comodines y
        de los número 8 y 9.
        """

        mazo = Mazo(False)
        stats = mazo.contar_cartas()

        self.assertEqual(len(mazo), 40)

        for i in range(1, 13):
            if i in (8, 9):
                num_esperado = 0
            else:
                num_esperado = 4
            self.assertEquals(stats[i], num_esperado)

        for palo in Palo:
            if palo == Palo.COMODIN:
                num_esperado = 0
            else:
                num_esperado = 10
            self.assertEqual(stats[palo.value], num_esperado)


    def test_3_mazo_nunca_repetira_cartas(self) -> None:
        """
        Si se saca dos cartas cualesquiera del mazo, salvo en
        el caso que las dos sean los dos comodines de un mazo entero,
        dichas cartas nunca serán iguales.
        """

        for _ in range(1000):
            mazo_entero = Mazo(True)
            mazo_40 = Mazo(False)

            carta_1 = mazo_entero.get()
            carta_2 = mazo_entero.get()
            carta_3 = mazo_40.get()
            carta_4 = mazo_40.get()

            if carta_1.es_comodin() and carta_2.es_comodin():
                self.assertEqual(carta_1, carta_2)
            else:
                self.assertNotEqual(carta_1, carta_2)
            
            self.assertNotEqual(carta_3, carta_4)