"""
Vista genérica de un juego.
"""

from typing import TYPE_CHECKING, Any, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View

from .vista_reiniciar_abc import cerrar_partida

if TYPE_CHECKING:
    from discord import Message

    from ...botshot import BotShot
    from ...db import CursorDesc
    from ..jugador import Jugador
    from ..modelos import JuegoBase
    from ..registradores import RegistradorBase


class BotonCerrar(Button):
    """
    Botón para cerrar la partida.
    """

    def __init__(self, id_boton: str) -> None:
        """
        Inicializa el botón para cerrar.
        """

        super().__init__(label="Cerrar",
                         custom_id=id_boton,
                         style=ButtonStyle.gray,
                         emoji=Emoji.from_str("\U0001F6D1"),
                         row=4)


    async def callback(self, interaction: Interaction) -> Any:
        """
        Cierra la partida.
        """

        await cerrar_partida(interaction)


class VistaJuegoBase(View):
    """
    Clase de vista para un juego.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase",
                 registrador: Optional["RegistradorBase"],
                 mensaje_raiz: Optional["Message"]) -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(timeout=None)

        self.bot: "BotShot" = bot
        self.modelo: "JuegoBase" = modelo
        self.registrador: Optional["RegistradorBase"] = registrador
        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        if self.agregar_boton_cerrar():
            self.add_item(BotonCerrar(self.get_cerrar_id()))

        self.modelo.setup()


    async def on_timeout(self) -> None:
        """
        Pasó el tiempo.
        """

        self.clear_items()
        if self.mensaje_raiz is not None:
            await self.mensaje_raiz.edit(content="*Tiempo agotado. Cerrando...*",
                                         delete_after=5.0)


    async def setup(self) -> None:
        """
        Acciones a realizar justo al inciarse la partida, NO
        al inicializarse la instancia junto con el manejador.

        Por default no hace nada.
        """

        return


    def clonar(self) -> "VistaJuegoBase":
        """
        Devuelve una copia, reiniciada del mismo.
        """

        return type(self)(self.bot,
                          self.modelo,
                          self.registrador,
                          self.mensaje_raiz)


    @staticmethod
    def agregar_boton_cerrar() -> bool:
        """
        Decide si agregar un botón para cerrar la vista.

        Subclases pueden sobreescribir esto para cambiarlo.
        """

        return True


    @staticmethod
    def get_cerrar_id() -> str:
        """
        El ID del botón para cerrar la vista.
        """

        return "game_close"


    def existe_jugador(self, *, id_jugador: str) -> bool:
        """
        Basado en el id de un jugador, decide si el pasado está
        entre los jugadores actuales.
        """

        return self.modelo.existe_jugador(id_jugador=id_jugador)


    def get_jugador(self, id_jugador: str) -> Optional["Jugador"]:
        """
        Devuelve un jugador unido según el ID, si lo encuentra.

        Sino devuelve `None`.
        """

        return self.modelo.get_jugador(id_jugador)


    def refrescar_datos(self, *, id_jugador: str, **kwargs) -> "CursorDesc":
        """
        Refresca los datos como las estadísticas
        en la DB.
        """

        if self.registrador is not None:
            self.registrador.refrescar_datos(id_jugador=id_jugador, **kwargs)
