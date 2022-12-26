"""
Cog para comandos que trabajan con audio.
"""

from typing import TYPE_CHECKING, Optional

from discord import Attachment, ChannelType, FFmpegPCMAudio, Interaction
from discord.app_commands import Choice, autocomplete, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from ..auxiliares import autocompletado_canales_voz
from ..constantes import DEV_ROLE_ID
from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot
    from discord.abc import Messageable


class CogAudio(_CogABC):
    """
    Cog para comandos de audio.
    """

    @appcommand(name="conectar",
                description="Conecta a un canal de voz.")
    @describe(canal="El canal al que conectarse.")
    @has_role(DEV_ROLE_ID)
    @autocomplete(canal=autocompletado_canales_voz)
    async def conectar_channel(self, interaccion: Interaction, canal: Optional[str]=None) -> None:
        """
        Conecta a un canal de voz.
        """

        if canal is None:
            canal: "Messageable" = interaccion.channel
        else:
            canal: "Messageable" = interaccion.guild.get_channel(int(canal))

        if canal.type != ChannelType.voice:
            await interaccion.response.send_message(content="Este no es un canal de voz.",
                                                    ephemeral=True)
            return


        await canal.connect()
        await interaccion.response.send_message(content="Ya me conecté!",
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
    @describe(sonido="El sonido a reproducir.",
              archivo="Un archivo a reproducir.")
    @has_role(DEV_ROLE_ID)
    @choices(sonido=[Choice(name="camioncito1", value="camioncito1"),
                    Choice(name="camioncito2", value="camioncito2"),
                    Choice(name="hay_wa", value="hay_wa")])
    async def reproducir_sonido(self,
                                interaccion: Interaction,
                                sonido: Optional[Choice[str]]=None,
                                archivo: Optional[Attachment]=None) -> None:
        """
        Reproduce un sonido, ya sea precargado o de archivo.
        """
        if sonido is None == archivo is None:
            await interaccion.response.send_message("`sonido` o `archivo` deben estar presentes," +
                                                    "pero no ninguno o ambos a la vez.",
                                                    ephemeral=True)
            return

        if interaccion.guild.voice_client is None:
            await interaccion.response.send_message(content="No estoy conectado a ningún canal.",
                                                    ephemeral=True)
            return

        if sonido is not None:
            await self._reproducir_sonido_cargado(interaccion, sonido.value)
        
        elif archivo is not None:
            await self._reproducir_archivo_sonido(interaccion, archivo)


    async def _reproducir_sonido_cargado(self, interaccion: Interaction, nombre_sonido: str) -> None:
        """
        Reproduce un sonido buscándolo en las carpetas que botshot tiene.
        """
        obj_sonido = FFmpegPCMAudio(f"sounds/{nombre_sonido}.mp3")
        interaccion.guild.voice_client.play(obj_sonido)      

        await interaccion.response.send_message(content="Reproduciendo sonido...",
                                                ephemeral=True)


    async def _reproducir_archivo_sonido(self, interaccion: Interaction, archivo: Attachment) -> None:
        """
        Reproduce un sonido proveniente de un archivo subido.
        """

        if "audio" not in archivo.content_type:
            await interaccion.response.send_message(content="Capo, esto no es un audio.",
                                                    ephemeral=True)
            return

        arch_sonido = await archivo.to_file()
        obj_sonido = FFmpegPCMAudio(arch_sonido.fp, pipe=True)
        interaccion.guild.voice_client.play(obj_sonido)

        await interaccion.response.send_message(content="Reproduciendo sonido...",
                                                ephemeral=True)



async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """
    await bot.add_cog(CogAudio(bot))
