"""
Módulo para un juego de 4 en Línea.
"""

from random import choice, randint
from string import ascii_uppercase
from typing import TYPE_CHECKING, Optional, TypeAlias

from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import Jugador, ListaJugadores
    from ..opciones import OpcionesBase

Grilla: TypeAlias = list[list["Casilla"]]

ROJO: str = "\U0001F534"
AMARILLO: str = "\U0001F7E1"
CIRCULOS: tuple[str, ...] = (ROJO, AMARILLO)
VACIO: str = ""

FICHA_ROJA: str = "#F02311"
FICHA_AMARILLA: str = "#F0D53C"


class Casilla:
    """
    Clase para gaurdar datos en una casilla.
    """

    def __init__(self, contenido: str=VACIO, /) -> None:
        """
        Inicializa una casilla.
        """

        self._cont: str = contenido
        self.vecinos: list[list[int]] = [[0 for _ in range(3)] for _ in range(3)]


    def __str__(self) -> str:
        """
        Devuelve una representación para imprimir de la casilla.
        """

        return f"({(self.contenido() if self.contenido() != VACIO else '-')})"


    def contenido(self) -> str:
        """
        Devuelve el contenido de la casilla.
        """

        return self._cont


    def cambiar_contenido(self, nuevo_contenido: str) -> None:
        """
        Cambia el contenido de la casilla.
        """

        self._cont = nuevo_contenido


class CuatroEnLinea(JuegoBase):
    """
    Juego de 4 en Línea.
    """

    nombre_muestra: str = "4 en Línea"
    descripcion: str = "Deja caer letras en el tablero y logra alinear 4 en un tablero 7x6."
    emojis_muestra: tuple[str, ...] = CIRCULOS
    min_jugadores: int = 2
    max_jugadores: int = 2


    @staticmethod
    def color_random() -> str:
        """
        Devuelve un string en el formato #FFFFFF.
        """

        num =  f"{randint(0x000000, 0xFFFFFF):X}".zfill(6)
        return f"#{num}"


    def elegir_color(self, repetidos: tuple[str, ...]=tuple()) -> str:
        """
        Devuelve un color, asegurándose de que no está repetido
        en 'repetidos'.
        """

        color = self.color_random()

        while color in repetidos:
            color = self.color_random()

        return color


    @staticmethod
    def letra_random() -> str:
        """
        Devuelve una letra mayúscula aleatoria.
        """

        return choice(ascii_uppercase)


    def elegir_letra(self, repetidos: tuple[str, ...]=tuple()) -> str:
        """
        Devuelve un letra, asegurándose de que no está repetido
        en 'repetidos'.
        """

        letra = self.letra_random()

        while letra in repetidos:
            letra = self.letra_random()

        return letra


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        if len(self.jugadores) != 2:
            raise ValueError("Más de dos jugadores están jugando 4 en Línea.")

        self.jugador_1, self.jugador_2 = self.jugadores

        self.letra_1: str = self.elegir_letra()
        self.letra_2: str = self.elegir_letra((self.letra_1,))

        if self.opciones.colores_default:
            self.color_1: str = FICHA_ROJA
            self.color_2: str = FICHA_AMARILLA
        else:
            self.color_1: str = self.elegir_color()
            self.color_2: str = self.elegir_color((self.color_1,))

        self.turno: int = 0
        self.dim_x: int = 7
        self.dim_y: int = 6
        self.n : int = 4 # Las fichas a alinear para ganar
        self.grilla: Grilla = self._generar_grilla(self.dim_x, self.dim_y)
        self.ultima_ficha: Optional[tuple[int, int]] = None

        self._terminado: bool = False
        self._empate: bool = False


    def __repr__(self) -> str:
        """
        Devuelve una representación de la grilla.
        """

        return str([[str(casilla) for casilla in fila] for fila in self.grilla])


    def __str__(self) -> str:
        """
        Devuelve una representación para imprimir de la grilla.
        """

        tablero = "\n".join([
                str("\t".join(
                    [(casilla.contenido() if casilla.contenido() != VACIO else "-")
                     for casilla in fila]
                    )
                )
                for fila in self.grilla
            ]
        )
        indices = '\t'.join([str(n) for n in range(1, self.dim_x + 1)])

        return f"{tablero}\n{indices}"


    def _generar_grilla(self, dim_x: int, dim_y: int) -> Grilla:
        """
        Genera la grilla.
        """

        return [[Casilla(VACIO) for _ in range(dim_x)] for _ in range(dim_y)]


    def _validar_col(self, col: int) -> bool:
        """
        Determina si un número de columna está fuera o dentro de
        los límites de la grilla.
        """

        return 0 <= col <= (self.dim_x - 1)


    def _validar_fil(self, fil: int) -> bool:
        """
        Determina si un número de fil está fuera o dentro de
        los límites de la grilla.
        """

        return 0 <= fil <= (self.dim_y - 1)


    def _validar_coords(self, col: int, fil: int) -> bool:
        """
        Determina si unas coordenadas están dentro de los
        límites de la grilla.
        """

        return self._validar_col(col) and self._validar_fil(fil)


    def _turno_par(self) -> bool:
        """
        Es un turno par.
        """

        return self.turno % 2 == 0


    def _turno_impar(self) -> bool:
        """
        Es un turno impar.
        """

        return self.turno % 2 == 1


    @property
    def jugador_actual(self) -> "Jugador":
        """
        Devuelve un jugador según el turno actual.
        """

        if self.opciones is None or self.opciones.primero_jugador_1:
            return self.jugadores[(self.turno % 2)]

        return self.jugadores[(self.turno % 2) - 1]


    @property
    def jugador_anterior(self) -> "Jugador":
        """
        Devuelve un jugador según el turno anterior.
        """

        if self.opciones is None or self.opciones.primero_jugador_1:
            return self.jugadores[(self.turno % 2) - 1]

        return self.jugadores[(self.turno % 2)]


    def _orden_letras(self) -> tuple[str, str]:
        """
        Devuelve una tupla indicando qué letra debería
        ir primero y cuál después.
        """

        if self.opciones is None or self.opciones.primero_jugador_1:
            return (self.letra_1, self.letra_2)

        return (self.letra_2, self.letra_1)


    @property
    def letra_actual(self) -> str:
        """
        Devuelve una letra de un jugador según el turno actual.
        """

        prim, seg = self._orden_letras()

        return (prim
                if self._turno_par()
                else seg)


    def _orden_colores(self) -> tuple[str, str]:
        """
        Devuelve una tupla indicando qué color debería
        ir primero y cuál después.
        """

        if self.opciones is None or self.opciones.primero_jugador_1:
            return (self.color_1, self.color_2)

        return (self.color_2, self.color_1)


    @property
    def color_actual(self) -> str:
        """
        Devuelve un color de un jugador según el turno actual.
        """

        prim, seg = self._orden_colores()

        return (prim
                if self._turno_par()
                else seg)


    @property
    def color_anterior(self) -> str:
        """
        Devuelve un color de un jugador según el turno anterior.
        """

        prim, seg = self._orden_colores()

        return (prim
                if self._turno_impar()
                else seg)


    def _refrescar_mensaje_turno(self) -> None:
        """
        Refresca el mensaje que indica los turnos.
        """

        self.mensaje =  f"Turno de **{self.jugador_actual.nombre}"
        self.mensaje += (f" [ {self.letra_actual} ]**\n```\n{str(self)}\n```"
                         if self.opciones.modo_texto
                         else "**")


    def iniciar(self, *_args, **_kwargs) -> bool:
        """
        Inicia el juego.
        """

        self._refrescar_mensaje_turno()
        return True


    def _casilla_obj(self, col: int, fil: int) -> Casilla:
        """
        Devuelve el objeto casilla en unas coordenadas.
        """

        return self.grilla[fil][col]


    def casilla(self, col: int, fil: int) -> str:
        """
        Devuelve una casilla en las coordenadas puestas.
        """

        return self._casilla_obj(col, fil).contenido()


    def casilla_esta_libre(self, col: int, fil: int) -> bool:
        """
        Determina si en las coordenadas puestas no hay ya
        colocada una letra.
        """

        return self.casilla(col, fil) == VACIO


    def fila_libre(self, col: int) -> int:
        """
        Dada una columna, devuelve el número de fila que
        todavía no fue ocupado, o `-1` si no la hay.

        Se da por hecho que el número de columna es válido.
        """

        fila = -1

        for fil in range(self.dim_y):
            if self.casilla_esta_libre(col, fil):
                fila += 1

        return fila


    def col_esta_llena(self, col: int) -> bool:
        """
        Determina si una columna está llena.
        """

        return self.fila_libre(col) < 0


    def dejar_caer(self, col: int) -> None:
        """
        Suelta la letra en alguna columna.
        """

        if not self._validar_col(col):
            raise ValueError(f"Número de columna `{col}` no válido.")

        if self.col_esta_llena(col):
            return

        fil_libre = self.fila_libre(col)
        self._casilla_obj(col, fil_libre).cambiar_contenido(self.letra_actual)
        self.ultima_ficha = (col, fil_libre)
        self.actualizar_vecinos(col, fil_libre)

        self.verificar_fin(col, fil_libre)


    def actualizar_vecinos(self, col: int, fil: int) -> None:
        """
        Actualiza el número de vecinos de todas las casillas
        alrededor de la indicada.
        """

        if not self._validar_coords(col, fil):
            return
        
        cas = self._casilla_obj(col, fil)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == dy == 0: # No checkearse uno mismo
                    continue
                # +1 para cambiar -1=0=1 a 0=1=2 como indices
                cas.vecinos[dy + 1][dx + 1] = self._verificar_direccion(col, fil, dx, dy, True)


    def _verificar_direccion(self,
                             col: int,
                             fil: int,
                             dx: int,
                             dy: int,
                             actualizar_vecinos: bool=True) -> int:
        """
        Indica la cantidad de vecinos del mismo tipo que hay en una una dirección,
        SIN CONTAR la que ya está en ('col', 'fil').
        """

        if self._es_letra_actual(col + dx, fil + dy):
            if actualizar_vecinos:
                ady = self._casilla_obj(col + dx, fil + dy)
                ady.vecinos[-dy + 1][-dx + 1] = self._verificar_direccion(col + dx,
                                                                          fil + dy,
                                                                          -dx,
                                                                          -dy,
                                                                          False)
            return self._verificar_direccion(col + dx, fil + dy, dx, dy, actualizar_vecinos) + 1

        return 0


    def actualizar(self, *_args, **kwargs) -> bool:
        """
        Actualiza el juego.
        """

        estado = False

        if self.terminado():
            return estado

        col = kwargs.get("col")

        if self.col_esta_llena(col):
            self.mensaje = "*Movimiento Inválido.*"
            estado = False

        else:
            self.dejar_caer(col)
            if not self.terminado(): self.turno += 1
            self._refrescar_mensaje_turno()
            estado = True

        return estado


    def terminado(self) -> bool:
        """
        Determina si el juego está acabado.
        """

        return self._terminado


    def empate(self) -> bool:
        """
        Un método opcional para determinar si
        el juego terminó en empate.

        Por defecto devuelve `False`.
        """

        return self._empate


    def _es_letra_actual(self, col: int, fil: int) -> bool:
        """
        Determina si una letra en una casilla es la misma
        que la del turno actual.
        """

        if not self._validar_coords(col, fil):
            return False

        return self.casilla(col, fil) == self.letra_actual


    def verificar_fin(self, col: int, fil: int) -> None:
        """
        Analiza el tablero para indicar si el juego terminó.
        """

        if self.turno >= (self.dim_x * self.dim_y) - 1: # Todas las casillas llenas
            self._terminado = True
            self._empate = True
            return


        cas = self._casilla_obj(col, fil)

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == dy == 0:
                    continue

                if (cas.vecinos[dy + 1][dx + 1] + cas.vecinos[-dy + 1][-dx + 1] + 1) >= self.n:
                    self._terminado = True
                    return


    def reiniciar(self) -> None:
        """
        Reinicia el 4 en Línea.
        """

        self.grilla = self._generar_grilla(self.dim_x, self.dim_y)
        self.turno = 0

        self._terminado = False
        self._empate = 0

        self.iniciar()
        self.setup()
