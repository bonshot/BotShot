"""
Módulos para tests de la clase 'TaTeTi'..
"""

from unittest import TestCase

from src.main.juegos.jugador import Jugador
from src.main.juegos.modelos.tateti import O, TaTeTi, X
from src.main.juegos.opciones import OpcionesTaTeTi


class TestTaTeTi(TestCase):
    """
    Tests del Tres en Raya.
    """

    def setUp(self) -> None:
        """
        Crea los jugadores antes de cada partida.
        """

        self.jugador_1: Jugador = Jugador(nombre="Jugador 1", id="jug_1")
        self.jugador_2: Jugador = Jugador(nombre="Jugador 2", id="jug_2")


    def test_1_hay_comportamiento_default_si_no_hay_opciones(self) -> None:
        """
        Aún sin sus opciones, el modelo debería funcionar con parámetros
        predeterminados.
        """

        tateti = TaTeTi([self.jugador_1, self.jugador_2])

        self.assertIsNone(tateti.opciones)
        self.assertEqual(tateti.jugador_actual, self.jugador_1)
        self.assertEqual(tateti.ficha_actual, X)


    def test_2_no_pasa_de_nueve_turnos(self) -> None:
        """
        Al finalizar, no deberían haber pasado más de 9 turnos.
        """

        tateti = TaTeTi([self.jugador_1, self.jugador_2])

        for dx, dy in ((1, 1), (2, 1), (0, 0),    # x|o|x
                         (2, 2), (2, 0), (1, 0),    # x|x|o
                         (0, 1), (0, 2), (1, 2)):   # o|x|o
            self.assertLess(tateti.turno_actual, 9)
            tateti.actualizar(col=dx, fil=dy)

        # Comos los turnos empiezan en 0 (cero), el último turno debería quedar en 8 (ocho)
        self.assertEqual(tateti.turno_actual, 8)


    def test_3_verificar_emojis_predeterminados(self) -> None:
        """
        Si los jugadores no tienen emojis preferidos, los utilizados
        deberían ser las constantes impuestas en el mismo módulo.
        """

        tateti = TaTeTi([self.jugador_1, self.jugador_2])

        self.assertIsNone(self.jugador_1.emoji)
        self.assertIsNone(self.jugador_2.emoji)

        self.assertEqual(tateti.ficha_1, X)
        self.assertEqual(tateti.ficha_2, O)


    def test_4_la_partida_solo_acepta_dos_jugadores(self) -> None:
        """
        Sólo 2 (dos) jugadores pueden jugar al Tres en Raya.
        """

        jugador_3: Jugador = Jugador(nombre="Jugador 3", id="jug_3")

        with self.assertRaises(ValueError):
            TaTeTi([self.jugador_1, self.jugador_2, jugador_3])

        with self.assertRaises(ValueError):
            TaTeTi([jugador_3])

        tateti_bueno = TaTeTi([self.jugador_1, jugador_3])
        self.assertEqual(tateti_bueno.min_jugadores, 2)
        self.assertEqual(tateti_bueno.max_jugadores, 2)


    def test_5_partida_ganada_no_es_empate(self) -> None:
        """
        Una partida ganada normalmente no debería quedar marcada
        como 'empate'.
        """

        tateti = TaTeTi([self.jugador_1, self.jugador_2])

        # x|o|x
        # -|x|o
        # x|-|o
        for dx, dy in ((1, 1), (2, 2), (0, 0), (2, 1), (2, 0), (1, 0), (0, 2)):
            self.assertFalse(tateti.terminado())
            self.assertFalse(tateti.empate())
            tateti.actualizar(col=dx, fil=dy)

        self.assertTrue(tateti.terminado())
        self.assertFalse(tateti.empate())


    def test_6_partida_se_reinicia_correctamente(self) -> None:
        """
        Todos los parámetros vuelven correctamente a sus valores iniciales.
        """

        tateti = TaTeTi([self.jugador_1, self.jugador_2])

        # x|o|x
        # -|x|o
        # x|-|o
        for dx, dy in ((1, 1), (2, 2), (0, 0), (2, 1), (2, 0), (1, 0), (0, 2)):
            tateti.actualizar(col=dx, fil=dy)

        tateti.reiniciar()
        self.assertEqual(tateti.turno_actual, 0)
        self.assertFalse(tateti.terminado())
        self.assertFalse(tateti.empate())


    def test_7_segunda_partida_empieza_por_el_segundo_jugador(self) -> None:
        """
        En subsecuentes reinicios, los jugadores se van turnando por ver quién empieza primero.
        """

        jugadores = [self.jugador_1, self.jugador_2]
        fichas = (X, O)
        tateti = TaTeTi(jugadores, OpcionesTaTeTi())

        self.assertIsNotNone(tateti.opciones)

        for i in range(100): # Iteraciones arbitrariamente abundantes
            self.assertEqual(tateti.ficha_actual, fichas[i % 2])
            self.assertEqual(tateti.jugador_actual, jugadores[i % 2])

            # ganar
            for dx, dy in ((1, 1), (2, 2), (0, 0), (2, 1), (2, 0), (1, 0), (0, 2)):
                tateti.actualizar(col=dx, fil=dy)

            tateti.opciones.cambiar_orden_jugadores()
            tateti.reiniciar()


    def test_8_modelo_usa_emojis_preferidos(self) -> None:
        """
        Si un jugador tiene impuesto un emoji preferido, se utiliza ese
        en su lugar.
        """

        fuego = "\U0001F525"
        self.jugador_1.emoji = fuego
        tateti = TaTeTi([self.jugador_1, self.jugador_2], OpcionesTaTeTi())

        self.assertIsNotNone(self.jugador_1.emoji)
        self.assertIsNone(self.jugador_2.emoji)

        self.assertEqual(tateti.ficha_actual, fuego)
        self.assertEqual(tateti.ficha_anterior, O)

        # ganar y reiniciar
        for dx, dy in ((1, 1), (2, 2), (0, 0), (2, 1), (2, 0), (1, 0), (0, 2)):
            tateti.actualizar(col=dx, fil=dy)

        tateti.opciones.cambiar_orden_jugadores()
        tateti.reiniciar()

        self.assertEqual(tateti.ficha_actual, O)
        self.assertEqual(tateti.ficha_anterior, fuego)
