"""
Cog para comandos de inteligencia artificial.
"""
from typing import TYPE_CHECKING
from ...ia import farenheit as f
from ..cog_abc import _CogABC
from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe

if TYPE_CHECKING:
    from ...botshot import BotShot

class CogIA(_CogABC):
    """
    Cog para comandos de inteligencia artificial.
    """
    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia '_CogABC', o una hija.
        """
        super().__init__(bot)

    @appcommand(name='farenheit',
                description='Convierte grados Celsius a Farenheit mediante inteligencia artificial.')
    @describe(celsius="La cantidad de grados Celsius a convertir.")
    @describe(iteraciones="El número de iteraciones para el entrenamiento de la red neuronal, a más iteraciones, más preciso el resultado.")
    async def farenheit(self, interaccion: Interaction, celsius: float, iteraciones: int) -> None:
        """
        Convierte grados Celsius a Farenheit mediante inteligencia artificial.
        """
        if iteraciones < 1 or iteraciones > 887:
            await interaccion.response.send_message("El número de iteraciones debe ser mayor a 0 y menor a 10000.")
            return
        tiempo_entrenamiento, fahrenheit = f.convertir_celsius_a_fahrenheit(celsius, iteraciones)
        await interaccion.response.send_message(
            f"_**{celsius}ºC**_ son aproximadamente _**{fahrenheit[0][0]}ºF**_ _(con {iteraciones} entrenamientos)_.\nEl modelo se entrenó en _**{tiempo_entrenamiento}**_ segundos.")

async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """
    await bot.add_cog(CogIA(bot))