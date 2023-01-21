"""
Módulo para un juego de Piedra, Papel o Tijeras.
"""

from enum import Enum
from typing import TYPE_CHECKING, Optional

from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import ListaJugadores, Jugador
    from ..opciones import OpcionesBase

EMOJI_PIEDRA: str = "\U0001FAA8"
EMOJI_PAPEL: str = "\U0001F9FB"
EMOJI_TIJERAS: str = "\U00002702"


class EleccionPPT(Enum):
    """
    Enumeración de elecciones de una partida de
    Piedra, Papel o Tijeras.
    """

    PIEDRA = 0
    PAPEL = 1
    TIJERAS = 2


class PPT(JuegoBase):
    """
    Juego de Piedra, Papel o Tijeras.
    """

    nombre_muestra: str = "Piedra, Papel o Tijeras"
    descripcion: str = "Vence a tu oponente: Piedra > Tijeras, Tijeras > Papel, Papel > Piedra."
    emojis_muestra: tuple[str, ...] = (EMOJI_PIEDRA, EMOJI_PAPEL, EMOJI_TIJERAS)
    min_jugadores: int = 2
    max_jugadores: int = 2


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        if len(self.jugadores) != 2:
            raise ValueError("Más de dos jugadores están jugando Piedra, Papel o Tijeras.")

        jugador_1, jugador_2 = self.jugadores

        self.eleccion_1: Optional[EleccionPPT] = None
        self.eleccion_2: Optional[EleccionPPT] = None

        self.grilla_win: list[list["Jugador"]] = [
            # PIEDRA - PAPEL - TIJERAS
            [None, jugador_2, jugador_1], # PIEDRA
            [jugador_1, None, jugador_2], # PAPEL
            [jugador_2, jugador_1, None] # TIJERAS
        ]

        self._terminado: bool = False
        self._empate: bool = False


    def _ya_decidieron(self) -> bool:
        """
        Determina si ambos jugadores decidieron su jugada.
        """

        return self.eleccion_1 is not None and self.eleccion_2 is not None


    def iniciar(self, *_args, **_kwargs) -> bool:
        """
        Inicia el juego.
        """

        self.mensaje =  "**¡Cada uno elija!** Piedra, Papel o Tijeras."
        return True


    def actualizar(self, *_args, **_kwargs) -> bool:
        """
        Actualiza el juego.
        """

        self.verificar_win()
        return self._ya_decidieron()


    def terminado(self) -> bool:
        """
        Determina si el juego está acabado.
        """

        return self._terminado


    def empate(self) -> bool:
        """
        Determina si el juego acabó en empate.
        """

        return self._empate


    def decidir_1(self, eleccion: EleccionPPT) -> None:
        """
        Cambia la elección del jugador 1.
        """

        self.eleccion_1 = eleccion
        jugador_1 = self.jugadores[0]
        self.mensaje = f"¡**{jugador_1.nombre}** ya decidió!"


    def decidir_2(self, eleccion: EleccionPPT) -> None:
        """
        Cambia la elección del jugador 2.
        """

        self.eleccion_2 = eleccion
        jugador_2 = self.jugadores[1]
        self.mensaje = f"¡**{jugador_2.nombre}** ya decidió!"


    def determinar_ganador(self) -> Optional["Jugador"]:
        """
        Determina qué jugador ganó la ronda, y lo devuelve.
        Devuelve `None` si fue empate.

        Se da por hecho que ambos jugadores ya decidieron.
        """

        return self.grilla_win[self.eleccion_1.value][self.eleccion_2.value]


    def determinar_perdedor(self) -> Optional["Jugador"]:
        """
        Determina qué jugador perdió la ronda, y lo devuelve.
        Devuelve `None` si fue empate.

        Se da por hecho que ambos jugadores ya decidieron.
        """

        return self.grilla_win[self.eleccion_2.value][self.eleccion_1.value]


    def verificar_win(self) -> None:
        """
        Verifica si el juego terminó.
        """

        if not self._ya_decidieron():
            return

        res = self.determinar_ganador()

        if res is None:
            self._empate = True
        self._terminado = True


    def reiniciar(self) -> None:
        """
        Reinicia para comenzar otra ronda.
        """

        self.eleccion_1 = None
        self.eleccion_2 = None

        self._terminado: bool = False
        self._empate: bool = False

        self.iniciar()
        self.setup()
