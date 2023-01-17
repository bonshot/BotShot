"""
Vista genérica de las opciones de un juego.
"""

from typing import TYPE_CHECKING, Optional

from discord import Interaction, ButtonStyle, PartialEmoji as Emoji
from discord.ui import Button, button

from .paginador import Paginador

if TYPE_CHECKING:
    from ...botshot import BotShot
    from ...interfaces.juegos import Lobby
    from ..modelos import OpcionesBase


class VistaOpcionesBase(Paginador):
    """
    Clase de vista para las opciones de un juego.
    """

    max_elementos_por_pagina: int = 5

    def __init__(self,
                 bot: "BotShot",
                 opciones: "OpcionesBase",
                 menu_anterior: Optional["Lobby"]=None) -> None:
        """
        Inicializa una instancia de una vista de opciones.
        """

        self.bot: "BotShot" = bot
        self.opciones: "OpcionesBase" = opciones
        self.menu_anterior: Optional["Lobby"] = menu_anterior

        super().__init__(self.opciones.propiedades(),
                         timeout=None)


    @button(label="Volver",
            custom_id="options_go_back",
            disabled=False,
            style=ButtonStyle.gray,
            emoji=Emoji.from_str("\U000021A9"),
            row=4)
    async def volver_al_lobby(self, interraccion: Interaction, _boton: Button) -> None:
        """
        Vuelve al lobby.
        """

        if self.menu_anterior is not None:
            await interraccion.response.edit_message(view=self.menu_anterior)
            return

        await interraccion.response.edit_message(content="*No hay un lobby asignado...*")
