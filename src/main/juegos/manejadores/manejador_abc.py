"""
Módulo para manejador genérico de un juego.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, TypeAlias

from discord import Embed

if TYPE_CHECKING:

    from ..jugador import ListaJugadores
    from ..modelos import JuegoBase
    from ..opciones import OpcionesBase
    from ..vistas import VistaJuegoBase

ListaManejadores: TypeAlias = list[type["ManejadorBase"]]


class ManejadorBase(ABC):
    """
    Clase abstracta para manejar un juego.

    Un manejador conecta el modelo con su clase de parámetros, el lobby,
    y más de ser necesario.
    """

    _ignorar: bool = False
    lista_clases_manejadores: ListaManejadores = []


    def __init_subclass__(cls: type["ManejadorBase"]) -> None:
        """
        Registra un manejador.
        """

        if hasattr(cls, "_ignorar") and cls._ignorar is True:
            return

        __class__.lista_clases_manejadores.append(cls)


    def __init__(self,
                 *,
                 jugadores: "ListaJugadores",
                 min_jugadores: int=1,
                 max_jugadores: int=2,
                 **kwargs) -> None:
        """
        Inicializa el manejador del juego.
        """

        cls_opciones = self.clase_opciones()
        cls_vista_opciones = self.clase_vista_opciones()

        self.lista_jugadores: "ListaJugadores" = jugadores
        self.min_jugadores: int = min_jugadores
        self.max_jugadores: int = max_jugadores

        self._modelo_inst: Optional["JuegoBase"] = None
        self._vista_modelo_inst: Optional["VistaJuegoBase"] = None
        self._opciones_inst : Optional["OpcionesBase"] = (cls_opciones(**kwargs)
                                                          if cls_opciones is not None
                                                          else None)
        self._vista_opciones_inst: Optional["VistaJuegoBase"] = (
                                                            cls_vista_opciones(self._opciones_inst)
                                                            if (cls_opciones is not None
                                                                and cls_vista_opciones is not None)
                                                            else None)


    @staticmethod
    @abstractmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return NotImplementedError


    @staticmethod
    @abstractmethod
    def clase_vista_modelo() -> "VistaJuegoBase":
        """
        Devuelve la vista asignado al modelo.
        """

        raise NotImplementedError


    @staticmethod
    def clase_opciones() -> Optional[type["OpcionesBase"]]:
        """
        Devuelve las opciones del juego, de tenerlas.

        A diferencia del modelo, no es obligatorio tener
        opciones.
        """

        return None


    @staticmethod
    def clase_vista_opciones() -> Optional["VistaJuegoBase"]:
        """
        Devuelve la vista de las opciones del juego.
        """

        return None


    @classmethod
    def nombre_juego(cls) -> str:
        """
        Devuelve el nombre para mostrar del modelo del juego.
        """

        return cls.clase_modelo().nombre_juego()


    @property
    def modelo(self) -> Optional["JuegoBase"]:
        """
        Devuelve la instancia del modelo asignado.
        """

        return self._modelo_inst


    @property
    def vista_modelo(self) -> Optional["VistaJuegoBase"]:
        """
        Devuelve la instancia de la vista del modelo.
        """

        return self._vista_modelo_inst


    def iniciar_modelo(self, **kwargs) -> None:
        """
        Inicializa el modelo en una instancia.
        """

        cls_modelo = self.clase_modelo()
        cls_vista_modelo = self.clase_vista_modelo()

        self._modelo_inst: "JuegoBase" = cls_modelo(self.lista_jugadores, **kwargs)
        self._modelo_inst.iniciar()
        self._vista_modelo_inst: "VistaJuegoBase" = cls_vista_modelo(self._modelo_inst)


    @property
    def opciones(self) -> Optional["OpcionesBase"]:
        """
        Devuelve la instancia de las opciones del juego asignado.
        """

        return self._opciones_inst


    @property
    def vista_opciones(self) -> Optional["VistaJuegoBase"]:
        """
        Devuelve la instancia de la vista de opciones.
        """

        return self._vista_opciones_inst


    def refrescar_embed(self) -> Embed:
        """
        Genera un nuevo embed con la información actual.
        """

        embed = Embed(title=f"Partida de {self.clase_modelo().nombre_juego()}")

        jugadores_esperando = "\n".join(
            list(f"- {(jugador.emoji if jugador.emoji is not None else '')} `{jugador.nombre}`"
                 for jugador in self.lista_jugadores
            )
        )

        subtitulo = (f"Jugadores en espera ({self.cantidad_jugadores}/{self.min_jugadores})" +
                     f"\tMax: {self.max_jugadores}")
        embed.add_field(name=subtitulo,
                        value=jugadores_esperando)

        return embed


    @property
    def cantidad_jugadores(self) -> int:
        """
        Devuelve la cantidad de jugadores actuales.
        """

        return len(self.lista_jugadores)


    def hay_suficientes(self) -> bool:
        """
        Determina si hay más jugadores unidos que el mínimo.
        """

        return self.cantidad_jugadores >= self.min_jugadores
