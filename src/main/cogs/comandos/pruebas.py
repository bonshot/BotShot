"""
Cog de comandos para hacer pruebas.
"""

from math import sqrt
from typing import TYPE_CHECKING, Generator

from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogPruebas(_CogABC):
    """
    Cog para comandos de pruebas.
    """

    @staticmethod
    def d_ang(num: int,
              ang: float=45.0,
              pres: int=5,
              rel_tol: float=0.05) -> Generator[float, None, None]:
        """
        Va cediendo los ángulos necesarios para rotar
        una mano de cartas.
        """

        act = ang
        dang = (2 * ang) / (num - 1)

        while act >= (-ang - rel_tol):
            cand = round(act, pres)
            yield (cand if abs(cand) > rel_tol else 0.0)
            act = round(act - dang, pres)


    @staticmethod
    def d_num(num: int) -> Generator[int, None, None]:
        """
        Va cediendo valores por los que calcular translaciones.
        """

        for i in range(num):
            mitad = num // 2
            cand = i - mitad
            if (cand >= 0) and (num % 2 == 0):
                yield cand + 1
            else:
                yield cand


    @appcommand(name='suma',
                description='Suma dos números enteros.')
    @describe(x="Primer número a sumar.",
              y="Segundo número a sumar.")
    async def suma(self, interaccion: Interaction, x: int, y: int) -> None:
        """
        Suma dos enteros y envía por el canal el resultado.
        """

        await interaccion.response.send_message(f'{x} + {y} = {x + y}')

    @appcommand(name="fib",
                description="Devuelve el elemento de psoición 'n' en la sucesión " +
                            "de fibonacci, en tiempo constante.")
    @describe(n="La posición del número a devolver.")
    async def fib(self, interaccion: Interaction, n: int) -> None:
        """
        Devuelve un número en la posición 'n' en la sucesión
        de fibonacci.
        """

        res = int((((1 + sqrt(5)) ** n) - ((1 - sqrt(5)) ** n)) / ((2 ** n) * sqrt(5)))
        await interaccion.response.send_message(f"Fib(**{n}**)  =  **{res}**")


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogPruebas(bot))
