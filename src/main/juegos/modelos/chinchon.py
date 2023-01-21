"""
Módulo para un juego de Chinchón.
"""

from typing import TYPE_CHECKING, Optional, TypeAlias

from ..utils import Carta, Mazo
from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import ListaJugadores
    from ..opciones import OpcionesBase

ListaPosiciones: TypeAlias = list[ListaJugadores]

MADERA: str = "\U0001FAB5" # Hace las de 'Basto'
TROFEO: str = "\U0000F3C6" # Hace las de 'Copa'
DAGA: str = "\U0001F5E1" # Hace las de 'Espada'
MONEDA: str = "\U0001FA99" # Hace las de 'Oro'
PALOS: tuple[str, ...] = (MADERA, TROFEO, DAGA, MONEDA)


class Chinchon(JuegoBase):
    """
    Clase para implementar un juego de Chinchón.
    """

    nombre_muestra: str = "Chinchón"
    descripcion: str = "Vence a tus amigos en el clásico 'Chinchón' de la baraja española."
    emojis_muestra: tuple[str, ...] = PALOS
    min_jugadores: int = 2
    max_jugadores: int = 4


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        self.turno: int = 0
        self.ronda: int = 0

        self.mazo: Mazo = Mazo(entero=True)

        self.puntajes: dict[str, int] = {}
        for jug in self.jugadores:
            self.puntajes[jug.id] = 0

        if self.opciones is None:
            self.tope: int = 101
            self.hay_puntaje_negativo: bool = False

        else:
            self.tope: int = self.opciones.tope
            self.hay_puntaje_negativo: bool = self.opciones.hay_puntaje_negativo

        self._terminado: bool = False
        self._posiciones: ListaJugadores = []
