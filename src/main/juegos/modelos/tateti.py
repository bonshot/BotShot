"""
Módulo para un juego de Tres en Raya.
"""

from typing import TYPE_CHECKING, Optional, TypeAlias

from ..jugador import ListaJugadores
from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import Jugador
    from ..opciones import OpcionesBase

Grilla: TypeAlias = list[list[str]]

X: str = "\U0000274C"
O: str = "\U00002B55"


class TaTeTi(JuegoBase):
    """
    Juego de Tres en Raya.
    """

    nombre_muestra: str = "Tres en Raya"
    min_jugadores: int = 2
    max_jugadores: int = 2


    def __init__(self,
                 jugadores: ListaJugadores,
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        if len(self.jugadores) != 2:
            raise ValueError("Más de dos jugadores están jugando Tres en Raya.")

        jugador_1, jugador_2 = self.jugadores

        self.dim: int = 3
        self.grilla: Grilla = self._generar_grilla(self.dim)
        self.turno_actual: int = 0
        self.ficha_1: str = jugador_1.emoji or X
        self.ficha_2: str = jugador_2.emoji or O

        self._terminado: bool = False
        self._empate: bool = False


    def __str__(self) -> str:
        """
        Devuelve una representación de la grilla.
        """

        return str(self.grilla)


    def _generar_grilla(self, dim: int) -> Grilla:
        """
        Genera la grilla.
        """

        return [["" for _ in range(dim)] for _ in range(dim)]


    def _validar_coord(self, x: int, y: int) -> bool:
        """
        Verifica si una coordenada está dentro de los límites
        de la grilla.
        """

        return (0 <= x <= (self.dim - 1)
                and 0 <= y <= (self.dim - 1))


    def _actualizar_mensaje_turno(self) -> None:
        """
        Refresca el mensaje que indica el turno.
        """

        self.mensaje = f"Turno de **{self.jugador_actual.nombre} [ {self.ficha_actual} ]**"


    def _turno_par(self) -> bool:
        """
        Es un turno par.
        """

        return self.turno_actual % 2 == 0


    def _turno_impar(self) -> bool:
        """
        Es un turno impar.
        """

        return self.turno_actual % 2 == 1


    @property
    def jugador_actual(self) -> "Jugador":
        """
        Devuelve un jugador según el turno actual.
        """

        if self.opciones is None or self.opciones.empieza_primer_jugador:
            return self.jugadores[(self.turno_actual % 2)]

        return self.jugadores[(self.turno_actual % 2) - 1]


    def _orden_fichas(self) -> tuple[str, str]:
        """
        Devuelve una tupla indicando qué ficha debería
        ir primero y cuál después.
        """

        if self.opciones is None or self.opciones.empieza_primer_jugador:
            return (self.ficha_1, self.ficha_2)

        return (self.ficha_2, self.ficha_1)


    @property
    def ficha_actual(self) -> str:
        """
        Devuelve una ficha de jugador según el turno actual.
        """

        prim, seg = self._orden_fichas()

        return (prim
                if self._turno_par()
                else seg)


    @property
    def ficha_anterior(self) -> str:
        """
        Devuelve una ficha de jugador según el turno anterior.
        """

        prim, seg = self._orden_fichas()

        return (prim
                if self._turno_impar()
                else seg)


    def _es_ficha_actual(self, col: int, fil: str) -> bool:
        """
        Verifica si la ficha en cuestión es la actual.
        """

        if not self._validar_coord(col, fil):
            return False

        return self.casilla(col, fil) == self.ficha_actual


    def terminado(self) -> bool:
        """
        Devuelve si terminó el juego.
        """

        return self._terminado


    def empate(self) -> bool:
        """
        Si el juego terminó, determina si fue
        empate o ganó alguien.
        """

        return self._empate


    def casilla(self, col: int, fil: int) -> str:
        """
        Devuelve el contenido de una casilla.
        """

        return self.grilla[fil][col]


    def casilla_esta_ocupada(self, col: int, fil: int) -> bool:
        """
        Define si una casilla de la grilla ya tiene una ficha puesta.
        """

        return self.casilla(col, fil) != ""


    def mover(self, col: int, fil: int) -> None:
        """
        Coloca una ficha en la grilla.
        """

        if not self._validar_coord(col, fil):
            raise ValueError(f"Coordenadas ({col}, {fil}) no válidas.")

        self.grilla[fil][col] = self.ficha_actual


    def iniciar(self, *_args, **_kwargs) -> bool:
        """
        Inicia el Tres en Raya.
        """

        self._actualizar_mensaje_turno()
        return True


    def actualizar(self, *_args, **kwargs) -> bool:
        """
        Actualiza el Tres en Raya.

        El estado determina si se colocó una ficha.
        """

        estado = False

        if self._terminado:
            return estado

        col = kwargs.get("col")
        fil = kwargs.get("fil")
        
        if not self.casilla_esta_ocupada(col, fil):
            self.mover(col, fil)
            self.verificar_win(col, fil)
            if not self.terminado(): self.turno_actual += 1
            self._actualizar_mensaje_turno()
            estado = True
        else:
            self.mensaje = "*Movimiento Inválido.*"
            estado = False

        return estado


    def verificar_win(self, col: int, fil: int) -> None:
        """
        Verifica si alguien ganó la partida.
        De ser así, modifica una flag que lo indica.
        """

        if self.turno_actual >= 8: # Todos las casillas están ocupadas
            self._terminado = True
            self._empate = True
            return

        cols = fils = diags = rdiags = 0
        n = self.dim - 1 # Siempre uno menos que la dimensión de la grilla
        for i in range(self.dim):
            if self._es_ficha_actual(col, i):
                cols += 1
            if self._es_ficha_actual(i, fil):
                fils += 1
            if self._es_ficha_actual(i, i):
                diags += 1
            if self._es_ficha_actual(i, n - i):
                rdiags += 1

        if (cols == self.dim or
            fils == self.dim or
            diags == self.dim or
            rdiags == self.dim):
            self._terminado = True


    def reiniciar(self) -> None:
        """
        Reinicia todos los parámetros del juego.
        """

        self.grilla: Grilla = self._generar_grilla(self.dim)
        self.turno_actual: int = 0

        self._terminado: bool = False
        self._empate: bool = False

        self.iniciar()
        self.setup()
