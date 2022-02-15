"""
Cog de comandos para hacer pruebas.
"""

from discord.ext.commands import command, Context

from categoria_comandos import CategoriaComandos

class CogPruebas(CategoriaComandos):
    """
    Cog para comandos de pruebas.
    """

    @command(name='suma', aliases=['plus', '+'], help='[PRUEBA] suma dos enteros')
    async def suma(self, ctx: Context, num1: int, num2: int) -> None:
        """
        Suma dos enteros y envía por el canal el resultado.
        """

        await ctx.send(f'{num1} + {num2} = {num1 + num2}')