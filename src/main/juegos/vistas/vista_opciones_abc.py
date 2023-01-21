"""
Vista genérica de las opciones de un juego.
"""

from typing import TYPE_CHECKING, Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from .paginador import Paginador

if TYPE_CHECKING:
    from discord import Message

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
                 mensaje_raiz: Optional["Message"],
                 menu_anterior: Optional["Lobby"]=None) -> None:
        """
        Inicializa una instancia de una vista de opciones.
        """

        self.bot: "BotShot" = bot
        self.opciones: "OpcionesBase" = opciones
        self.menu_anterior: Optional["Lobby"] = menu_anterior

        super().__init__(self.opciones.propiedades(),
                         mensaje_raiz=mensaje_raiz,
                         timeout=None)


    async def on_timeout(self) -> None:
        """
        Pasó el tiempo.
        """

        self.clear_items()
        if self.mensaje_raiz is not None:
            await self.mensaje_raiz.edit(content="*Tiempo agotado. Cerrando...*",
                                         delete_after=5.0)


    async def refrescar_opciones(self,
                                 interaccion: Interaction,
                                 boton: Button,
                                 msg: Optional[str]=None) -> None:
        """
        Refresca el mensaje de opciones.
        """

        self.refrescar()
        await self.refrescar_mensaje(interaccion=interaccion,
                                     mensaje=(f"Cambiado opción a `{boton.label}`..."
                                              if msg is None
                                              else msg))


    def refrescar_boton_binario(self, boton: Button, etiqueta: str, esta_activado: bool) -> None:
        """
        Actualiza un botón con un valor booleano.
        """

        if esta_activado:
            boton.label = f"{etiqueta} ON"
            boton.style = ButtonStyle.green

        else:
            boton.label = f"{etiqueta} OFF"
            boton.style = ButtonStyle.red


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
