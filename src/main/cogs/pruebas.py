"""
Cog de comandos para hacer pruebas.
"""

from typing import TYPE_CHECKING

from discord.ext.commands import Context, command

from .categoria_comandos import CategoriaComandos

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogPruebas(CategoriaComandos):
    """
    Cog para comandos de pruebas.
    """

    @command(name='suma',
             aliases=['plus', '+'],
             help='[PRUEBA] suma dos enteros')
    async def suma(self, ctx: Context, num1: int, num2: int) -> None:
        """
        Suma dos enteros y envía por el canal el resultado.
        """

        await ctx.send(f'{num1} + {num2} = {num1 + num2}')


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogPruebas(bot))
