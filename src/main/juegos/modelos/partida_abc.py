"""
Módulo para partida genérica de un juego.
"""

from abc import ABC, abstractmethod
from secrets import token_hex
from typing import TYPE_CHECKING, Optional, TypeAlias

if TYPE_CHECKING:
    from ..jugador import ListaJugadores

ListaJuegos: TypeAlias = list[type["JuegoBase"]]


class JuegoBase(ABC):
    """
    Clase abstracta para el modelo de un juego.
    """

    _ignorar: bool = False
    nombre_muestra: Optional[str] = None
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


    def __init__(self,
                 jugadores: "ListaJugadores",
                 **kwargs) -> None:
        """
        Inicializa la instancia de un juego.
        """

        self.id: str = token_hex(32)
        self.jugadores: "ListaJugadores" = jugadores

        self.mensaje: str = ""

        self.extras: dict = kwargs


    def setup(self) -> None:
        """
        Configuraciones iniciales que el juego puede hacer antes
        de iniciarse. Dichas operaciones no pueden depender de nada
        que no sea el propio modelo y por lo tanto no acepta parámetros.
        """

        return


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
