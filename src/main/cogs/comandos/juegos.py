"""
Cog para manejar comandos de juegos.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand

from ...interfaces import SelectorJuegos
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogJuegos(_CogABC):
    """
    Cog para comandos de manejar juegos.
    """

    @appcommand(name="jugar",
                description="Inicia una partida de algún juego.")
    async def inic_diversion(self, interaccion: Interaction) -> None:
        """
        Inicia algún juego.
        """

        await interaccion.response.send_message(content="*Iniciando menu...*",
                                                ephemeral=True)

        await interaccion.channel.send(content="Por favor elige un juego:",
                                       view=SelectorJuegos(self.bot))


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogJuegos(bot))
