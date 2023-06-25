"""
Módulo para manejador genérico de un juego.
"""

from abc import ABC, abstractmethod
from random import choice
from typing import TYPE_CHECKING, Optional, TypeAlias

from discord import Embed, User

if TYPE_CHECKING:

    from discord import Message

    from ...botshot import BotShot
    from ..jugador import Jugador, ListaJugadores
    from ..modelos import JuegoBase
    from ..opciones import OpcionesBase
    from ..registradores import RegistradorBase
    from ..vistas import VistaJuegoBase, VistaOpcionesBase

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
                 bot: "BotShot",
                 jugadores: "ListaJugadores",
                 usuario_creador: User,
                 mensaje_raiz: Optional["Message"],
                 **kwargs) -> None:
        """
        Inicializa el manejador del juego.
        """

        cls_opciones = self.clase_opciones()
        cls_vista_opciones = self.clase_vista_opciones()
        cls_registrador = self.clase_registrador()

        self.bot: "BotShot" = bot
        self.lista_jugadores: "ListaJugadores" = jugadores
        self.creador: User = usuario_creador
        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        self._modelo_inst: Optional["JuegoBase"] = None
        self._vista_modelo_inst: Optional["VistaJuegoBase"] = None
        self._opciones_inst : Optional["OpcionesBase"] = (cls_opciones(**kwargs)
                                                          if cls_opciones is not None
                                                          else None)
        self._vista_opciones_inst: Optional["VistaOpcionesBase"] = (
                cls_vista_opciones(self.bot, self._opciones_inst, self.mensaje_raiz)
                if (cls_opciones is not None
                    and cls_vista_opciones is not None)
                else None
        )
        self._registrador_inst: Optional["RegistradorBase"] = (
                cls_registrador(**kwargs)
                if (cls_registrador is not None)
                else None
        )

        self.extras: dict = kwargs


    @staticmethod
    @abstractmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return NotImplementedError


    @staticmethod
    @abstractmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
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
    def clase_vista_opciones() -> Optional[type["VistaOpcionesBase"]]:
        """
        Devuelve la vista de las opciones del juego.
        """

        return None


    @staticmethod
    def clase_registrador() -> Optional[type["RegistradorBase"]]:
        """
        Devuelve la clase de registrador asociada a este juego.
        """

        return None


    @classmethod
    def nombre_juego(cls) -> str:
        """
        Devuelve el nombre para mostrar del modelo del juego.
        """

        return cls.clase_modelo().nombre_juego()


    @classmethod
    def descripcion_juego(cls) -> Optional[str]:
        """
        Devuelve la descripción a mostrar del juego, si la hay.
        """

        return cls.clase_modelo().descripcion_juego()


    @classmethod
    def emojis_juego(cls) -> tuple[str, ...]:
        """
        Devuelve el emoji para mostrar del juego, si lo hay.
        """

        return cls.clase_modelo().emojis_juego()


    @classmethod
    def elegir_emoji(cls) -> Optional[str]:
        """
        Elige un emoji al azar entre los disponibles.
        """

        return cls.clase_modelo().elegir_emoji()


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

        self._modelo_inst: "JuegoBase" = cls_modelo(self.lista_jugadores, self.opciones, **kwargs)
        self._modelo_inst.iniciar()
        self._vista_modelo_inst: "VistaJuegoBase" = cls_vista_modelo(self.bot,
                                                                     self._modelo_inst,
                                                                     self._registrador_inst,
                                                                     self.mensaje_raiz)


    @property
    def opciones(self) -> Optional["OpcionesBase"]:
        """
        Devuelve la instancia de las opciones del juego asignado.
        """

        return self._opciones_inst


    @property
    def vista_opciones(self) -> Optional["VistaOpcionesBase"]:
        """
        Devuelve la instancia de la vista de opciones.
        """

        return self._vista_opciones_inst


    @property
    def registrador(self) -> Optional["RegistradorBase"]:
        """
        Devuelve el registrador asociado a este juego.
        """

        return self._registrador_inst


    @property
    def jugador_host(self) -> "Jugador":
        """
        Devuelve el jugador que hostea la partida.
        Siempre debería ser el primero de la lista.
        """

        return self.lista_jugadores[0]


    @property
    def min_jugadores(self) -> int:
        """
        Devuelve la cantidad mínima de jugadores.
        """

        return self.clase_modelo().min_jugadores


    @property
    def max_jugadores(self) -> int:
        """
        Devuelve la cantidad máxima de jugadores.
        """

        return self.clase_modelo().max_jugadores


    def _cumplido_random(self) -> str:
        """
        Suelta una frase al azar.
        """

        return choice((
            "", # Sí, un string vacío es una opción
            " la máquina",
            " el papu",
            " es el que",
            " el más capo(ronga)"
        ))


    def refrescar_embed(self) -> Embed:
        """
        Genera un nuevo embed con la información actual.
        """

        mostrar_nombre = self.clase_modelo().nombre_juego()
        descripcion = self.clase_modelo().descripcion_juego()
        emoji = self.clase_modelo().elegir_emoji()
        mostrar_emoji = '' if emoji is None else f"{emoji} "
        embed = Embed(title=(f"Partida de {mostrar_emoji}{mostrar_nombre}"),
                      description=f"{descripcion}\n-\n*Máx jug: **{self.max_jugadores}***")

        jugadores_esperando = "\n".join(
            list((f"- {(f'{jugador.emoji} ' if jugador.emoji is not None else ' ')}" +
                  f"`{jugador.nombre}`")
                 for jugador in self.lista_jugadores
            )
        )

        subtitulo = (f"Jugadores en espera ({self.cantidad_jugadores}/{self.min_jugadores})" +
                     ("\t-\t" if self.registrador is not None else ""))
        embed.add_field(name=subtitulo,
                        value=jugadores_esperando,
                        inline=True)
        
        if self.registrador is not None:
            embed = self.registrador.agregar_datos_a_embed(embed=embed,
                                                           jugadores=self.lista_jugadores)

        embed.set_footer(text=(f"{self.jugador_host.nombre}{self._cumplido_random()} " +
                                "hostea esta partida."),
                         icon_url=self.creador.display_avatar.url)

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


    def hay_opciones(self) -> bool:
        """
        Determina si las opciones y su vista son ambos existentes.
        """

        return self.opciones is not None and self.vista_opciones is not None
