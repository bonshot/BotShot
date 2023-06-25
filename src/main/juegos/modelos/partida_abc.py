"""
Módulo para partida genérica de un juego.
"""

from abc import ABC, abstractmethod
from random import choice
from secrets import token_hex
from typing import TYPE_CHECKING, Optional, TypeAlias

if TYPE_CHECKING:
    from ..jugador import Jugador, ListaJugadores
    from ..opciones import OpcionesBase

ListaJuegos: TypeAlias = list[type["JuegoBase"]]


class JuegoBase(ABC):
    """
    Clase abstracta para el modelo de un juego.
    """

    _ignorar: bool = False
    nombre_muestra: Optional[str] = None
    descripcion: Optional[str] = None # No más de 100 caracteres
    emojis_muestra: Optional[tuple[str, ...]] = None
    min_jugadores: int = 1
    max_jugadores: int = 2


    lista_juegos: ListaJuegos = []


    def __init_subclass__(cls: type["JuegoBase"]) -> None:
        """
        Registra una subclase.
        """

        if hasattr(cls, "_ignorar") and cls._ignorar is True:
            return

        __class__.lista_juegos.append(cls)


    @classmethod
    def nombre_juego(cls) -> str:
        """
        Devuelve el nombre para mostrar del juego.
        """

        return (cls.nombre_muestra if cls.nombre_muestra is not None else cls.__name__)


    @classmethod
    def descripcion_juego(cls) -> Optional[str]:
        """
        Devuelve la descripción a mostrar del juego, si la hay.
        """

        return cls.descripcion


    @classmethod
    def emojis_juego(cls) -> tuple[str, ...]:
        """
        Devuelve el emoji asignado al juego, si lo hay.
        """

        return cls.emojis_muestra
    

    @classmethod
    def elegir_emoji(cls) -> Optional[str]:
        """
        Elige un emoji aleatorio de los que hay disponibles.
        """

        emojis = cls.emojis_juego()
        return (emojis if emojis is None else choice(emojis))


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa la instancia de un juego.
        """

        self.id: str = token_hex(32)
        self.jugadores: "ListaJugadores" = jugadores
        self.opciones: Optional["OpcionesBase"] = opciones

        self.mensaje: str = ""

        self.extras: dict = kwargs


    def setup(self) -> None:
        """
        Configuraciones iniciales que el juego puede hacer antes
        de iniciarse. Dichas operaciones no pueden depender de nada
        que no sea el propio modelo y por lo tanto no acepta parámetros.
        """

        return


    @property
    def cantidad_jugadores(self) -> int:
        """
        Devuelve la cantidad de jugadores.
        """

        return len(self.jugadores)


    def existe_jugador(self, *, id_jugador: str) -> bool:
        """
        Basado en el id de un jugador, decide si el pasado está
        entre los jugadores actuales.
        """

        return self.get_jugador(id_jugador) is not None


    def get_jugador(self, id_jugador: str) -> Optional["Jugador"]:
        """
        Consigue un jugador por id.
        """

        for jugador in self.jugadores:
            if id_jugador == jugador.id:
                return jugador

        return None


    @abstractmethod
    def iniciar(self, *args, **kwargs) -> bool:
        """
        Inicia el juego.
        """

        raise NotImplementedError


    @abstractmethod
    def actualizar(self, *args, **kwargs) -> bool:
        """
        Actualiza el juego.
        """

        raise NotImplementedError


    @abstractmethod
    def terminado(self) -> bool:
        """
        Determina si el juego está acabado.
        """

        raise NotImplementedError


    def empate(self) -> bool:
        """
        Un método opcional para determinar si
        el juego terminó en empate.

        Por defecto devuelve `False`.
        """

        return False


    def reiniciar(self) -> None:
        """
        Método opcional para reinciar el juego.
        """

        return
