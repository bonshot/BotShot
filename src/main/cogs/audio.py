"""
Cog para comandos que trabajan con audio.
"""

from typing import Optional, TYPE_CHECKING

from discord import Interaction, FFmpegPCMAudio
from discord.app_commands import Choice, autocomplete, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from .cog_abc import _CogABC
from ..auxiliares import autocompletado_canales
from ..constantes import DEV_ROLE_ID

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogAudio(_CogABC):
    """
    Cog para comandos de audio.
    """

    @appcommand(name="conectar",
                description="Conecta a un canal.")
    @describe(canal="El canal al que conectarse.")
    @has_role(DEV_ROLE_ID)
    @autocomplete(canal=autocompletado_canales)
    async def conectar_channel(self, interaccion: Interaction, canal: Optional[str]=None) -> None:
        """
        Conecta a un canal de voz.
        """

        if canal is None:
            canal = interaccion.channel
        else:
            canal = interaccion.guild.get_channel(int(canal))

        await canal.connect()

        await interaccion.response.send_message(content="Ya ejecuté el comando!",
                                                ephemeral=True)


    @appcommand(name="desconectar",
                description="Desconecta del canal de voz en el que esté.")
    @has_role(DEV_ROLE_ID)
    async def desconectar_channel(self, interaccion: Interaction) -> None:
        """
        Desconecta de un canal.
        """
        if interaccion.guild.voice_client is None:
            await interaccion.response.send_message(content="No estoy conectado a ningún canal.",
                                                    ephemeral=True)
            return
        
        await interaccion.guild.voice_client.disconnect()
        await interaccion.response.send_message(content="Desconectado correctamente.",
                                                ephemeral=True)


    @appcommand(name="reproducir")
    @describe(sonido="El sonido a reproducir.")
    @has_role(DEV_ROLE_ID)
    @choices(sonido=[Choice(name="camioncito1", value="camioncito1"),
                    Choice(name="camioncito2", value="camioncito2"),
                    Choice(name="hay_wa", value="hay_wa")])
    async def reproducir_sonido(self, interaccion: Interaction, sonido: Choice[str]) -> None:
        """
        Reproduce un sonido.
        """
        if interaccion.guild.voice_client is None:
            await interaccion.response.send_message(content="No estoy conectado a ningún canal.")
            return

        arch_sonido = FFmpegPCMAudio(f"sounds/{sonido.value}.mp3")
        interaccion.guild.voice_client.play(arch_sonido)      

        await interaccion.response.send_message(content="Reproduciendo sonido...")  
        


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """
    await bot.add_cog(CogAudio(bot))
