"""
Cog para comandos que trabajan con audio.
"""

from typing import TYPE_CHECKING, Optional

from discord import Attachment, ChannelType, FFmpegPCMAudio, Interaction
from discord.app_commands import AppCommandError, autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.errors import CheckFailure

from ..auxiliares import (autocompletado_archivos_audio,
                          autocompletado_canales_voz)
from ..checks import es_usuario_autorizado
from ..db.atajos import existe_usuario_autorizado
from .cog_abc import GroupsList, _CogABC, _GrupoABC

if TYPE_CHECKING:

    from discord.abc import GuildChannel

    from ..botshot import BotShot


class GrupoAudio(_GrupoABC):
    """
    Grupo para comandos de audio.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia de 'GrupoAudio'.
        """

        super().__init__(bot,
                         name="audio",
                         description="Comandos para manipular audios y sonidos.")


    async def interaction_check(self, interaccion: Interaction) -> bool:
        """
        Verifica si el usuario está autorizado.
        """

        return ((interaccion.user.id == self.bot.owner_id)
                 or existe_usuario_autorizado(interaccion.user.id)
                and interaccion.guild.voice_client is not None)


    async def on_error(self, interaccion: Interaction, error: AppCommandError) -> None:
        """
        Avisa el usuario que un comando falló.
        """

        if isinstance(error, CheckFailure):
            if interaccion.guild.voice_client is None:
                await interaccion.response.send_message(content="No estoy conectado a ningún canal de voz.",
                                                        ephemeral=True)
            else:
                await interaccion.response.send_message((f"Emm, {interaccion.user.mention}, vos no tenés " +
                                                        "permiso para usar este comando."),
                                                        ephemeral=True)
            return

        raise error from error


    @appcommand(name="play",
                description="Reproduce un sonido.")
    @describe(sonido="El sonido a reproducir.",
              archivo="Un archivo a reproducir.")
    @autocomplete(sonido=autocompletado_archivos_audio)
    async def reproducir_sonido(self,
                                interaccion: Interaction,
                                sonido: Optional[str]=None,
                                archivo: Optional[Attachment]=None) -> None:
        """
        Reproduce un sonido, ya sea precargado o de archivo.
        """
        if sonido is None == archivo is None:
            await interaccion.response.send_message("`sonido` o `archivo` deben estar presentes," +
                                                    "pero no ninguno o ambos a la vez.",
                                                    ephemeral=True)
            return

        if sonido is not None:
            await self._reproducir_sonido_cargado(interaccion, sonido)
        
        elif archivo is not None:
            await self._reproducir_archivo_sonido(interaccion, archivo)


    async def _reproducir_sonido_cargado(self, interaccion: Interaction, ruta_sonido: str) -> None:
        """
        Reproduce un sonido buscándolo en las carpetas que botshot tiene.
        """
        obj_sonido = FFmpegPCMAudio(ruta_sonido)
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


    @appcommand(name="stop",
                description="Detiene un sonido.")
    async def parar_sonido(self,
                           interaccion: Interaction) -> None:
        """
        Si el bot está reproduciendo algo, detenerlo.
        """

        cl_voz = interaccion.guild.voice_client

        if not cl_voz.is_playing() and not cl_voz.is_paused():
            mensaje = "Capo, no estoy reproduciendo nada, y tampoco hay nada pausado."

        else:
            mensaje = f"*Parando la reproducción...*"

        cl_voz.stop()
        await interaccion.response.send_message(content=mensaje,
                                                ephemeral=True)


    @appcommand(name="pausa",
                description="Pausa/Resume el audio.")
    async def pausar_resumir_sonido(self,
                                    interaccion: Interaction) -> None:
        """
        Si el bot está reproduciendo algo, lo pausa, sino intenta
        resumir el audio.
        """

        cl_voz = interaccion.guild.voice_client

        if not cl_voz.is_playing() and not cl_voz.is_paused():
            mensaje = "Capo, no estoy reproduciendo nada, y nada encuentro pausado."
        else:
            if cl_voz.is_paused():
                mensaje = "*Resumiendo audio...*"
                cl_voz.resume()
            elif cl_voz.is_playing():
                mensaje = "*Audio pausado.*"
                cl_voz.pause()

        await interaccion.response.send_message(content=mensaje,
                                                ephemeral=True)


class CogAudio(_CogABC):
    """
    Cog para comandos de audio.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoAudio]


    @appcommand(name="conectar",
                description="Conecta a un canal de voz.")
    @describe(canal="El canal al que conectarse.")
    @autocomplete(canal=autocompletado_canales_voz)
    @es_usuario_autorizado()
    async def conectar_channel(self, interaccion: Interaction, canal: Optional[str]=None) -> None:
        """
        Conecta a un canal de voz.
        """

        if canal is None:
            canal: "GuildChannel" = interaccion.channel
        else:
            canal: "GuildChannel" = interaccion.guild.get_channel(int(canal))

        if canal.type != ChannelType.voice:
            await interaccion.response.send_message(content="Este no es un canal de voz.",
                                                    ephemeral=True)
            return

        cl_voz = canal.guild.voice_client
        es_mismo_canal = False

        if (cl_voz is not None
            and cl_voz.is_connected()):

            if cl_voz.channel == canal:
                es_mismo_canal = True

            if cl_voz.is_playing() or cl_voz.is_paused():
                await cl_voz.move_to(canal)

            else:
                await cl_voz.disconnect()
                await canal.connect()

        else: # Si se conecta por primera vez
            await canal.connect()

        await interaccion.response.send_message(content=f"Ya me {'reconecté' if es_mismo_canal else 'conecté'}!",
                                                ephemeral=True)

        self.bot.log.info(f"{'Reconectado' if es_mismo_canal else 'Conectado'} al canal de voz " +
                          f"{canal.name!r} en {canal.guild.name!r}.")


    @appcommand(name="desconectar",
                description="Desconecta del canal de voz en el que esté.")
    @es_usuario_autorizado()
    async def desconectar_channel(self, interaccion: Interaction) -> None:
        """
        Desconecta de un canal.
        """

        cl_voz = interaccion.guild.voice_client

        if cl_voz is None:
            await interaccion.response.send_message(content="No estoy conectado a ningún canal de voz.",
                                                    ephemeral=True)
            return

        if cl_voz.is_playing() or cl_voz.is_paused():
            cl_voz.stop()
        await cl_voz.disconnect()
        await interaccion.response.send_message(content="Desconectado correctamente.",
                                                ephemeral=True)

        canal = interaccion.channel
        self.bot.log.info(f"Desconectado del canal de voz {canal.name!r} en {canal.guild.name!r}.")


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """
    await bot.add_cog(CogAudio(bot))
