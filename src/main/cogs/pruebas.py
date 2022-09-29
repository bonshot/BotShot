"""
Cog de comandos para hacer pruebas.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe

from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogPruebas(_CogABC):
    """
    Cog para comandos de pruebas.
    """

    @appcommand(name='suma',
                description='[PRUEBA] Suma dos números enteros.')
    @describe(x="Primer número a sumar.",
              y="Segundo número a sumar.")
    async def suma(self, interaccion: Interaction, x: int, y: int) -> None:
        """
        Suma dos enteros y envía por el canal el resultado.
        """

        await interaccion.response.send_message(f'{x} + {y} = {x + y}')


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogPruebas(bot))
