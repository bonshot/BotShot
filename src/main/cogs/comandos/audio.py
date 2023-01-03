"""
Cog para comandos que trabajan con audio.
"""

from typing import TYPE_CHECKING, Optional

from discord import Attachment, ChannelType, FFmpegPCMAudio, Interaction
from discord.app_commands import AppCommandError, autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.errors import CheckFailure
from tinytag import TinyTag

from ...archivos import borrar_archivo, repite_nombre
from ...auxiliares import (autocompletado_archivos_audio,
                           autocompletado_canales_voz,
                           autocompletado_miembros_guild)
from ...checks import es_usuario_autorizado
from ...db.atajos import get_sonidos_path
from ...enums import RestriccionesSonido
from ..cog_abc import GroupsList, _CogABC, _GrupoABC

if TYPE_CHECKING:

    from os import PathLike

    from discord import Member
    from discord.abc import GuildChannel

    from ...botshot import BotShot


TAMANIO_MAXIMO_AUDIO: int = 8388608 # 8 MB en bytes
DURACION_MAXIMA_AUDIO: int = 8 # en segundos


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

        return (self.bot.es_admin(interaccion.user.id)
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


    async def _reproducir_sonido_cargado(self,
                                         interaccion: Interaction,
                                         ruta_sonido: str) -> None:
        """
        Reproduce un sonido buscándolo en las carpetas que botshot tiene.
        """
        obj_sonido = FFmpegPCMAudio(ruta_sonido)
        interaccion.guild.voice_client.play(obj_sonido)      

        await interaccion.response.send_message(content="Reproduciendo sonido...",
                                                ephemeral=True)


    async def _reproducir_archivo_sonido(self,
                                         interaccion: Interaction,
                                         archivo: Attachment) -> None:
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


class GrupoSonido(_GrupoABC):
    """
    Grupo para comandos de sonidos, que tanto no
    tienen que ver con controles del reproductor.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia de 'GrupoSonido'.
        """

        super().__init__(bot,
                         name="sonido",
                         description="Comandos para interactuar con sonidos en general.")


    @appcommand(name="agregar",
                description="Registra un nuevo sonido para un usuario.")
    @describe(audio="El sonido a procesar.",
              usuario="El usuario al que asignarle el nuevo audio.")
    @autocomplete(usuario=autocompletado_miembros_guild)
    async def agregar_sonido(self,
                             interaccion: Interaction,
                             audio: Attachment,
                             usuario: Optional[str]=None) -> None:
        """
        Agrega un sonido asignado a un usuario.
        """

        if (audio.content_type is None 
            or "audio" not in audio.content_type):

            await interaccion.response.send_message(content="*Este archivo no es de audio. >:(*",
                                                   ephemeral=True)
            return

        autor = interaccion.user

        if usuario is not None and not self.bot.es_admin(autor.id):
            await interaccion.response.send_message(content=f"{autor.mention}, señor, usted no " +
                                                     "tiene permiso para modificar los sonidos " +
                                                     "de los demás.",
                                                    ephemeral=True)
            return

        if usuario is None:
            usuario: "Member" = autor
        else:
            usuario: "Member" = interaccion.guild.get_member(int(usuario))

        audio_fn = audio.filename
        ruta_temp = repite_nombre(f"{get_sonidos_path()}/bienvenida/{usuario.id}/{audio_fn}")
        await audio.save(ruta_temp)
        resultado = self._analizar_archivo_audio(ruta_temp)

        if resultado:
            restrs = ""
            borrar_archivo(ruta_temp)
            for restr, err in resultado:
                restrs += f"\n\t- **{restr.value}:** {err}."

            mensaje = (f"**[ERROR]** El archivo no cumple con los requisitos.\n\n" +
                       f">>> Restricciones violadas:\n{restrs}")
        else:
            mensaje = f"Agregando sonido `{audio_fn}` para **{usuario.display_name}**..."

        await interaccion.response.send_message(content=mensaje,
                                                ephemeral=True)
        self.bot.log.info(mensaje)


    def _analizar_archivo_audio(self,
                                ruta_audio: "PathLike") -> list[tuple[RestriccionesSonido, str]]:
        """
        Analiza un archivo de audio.
        Devuelve una lista con las restricciones violadas que se encontraron, junto con un mensaje
        de error; o una lista vacía si el archivo pasa las pruebas.
        """

        resultado = []
        tags = TinyTag.get(ruta_audio)

        if tags.filesize > TAMANIO_MAXIMO_AUDIO: # No más de 8 MB
            mb = 1048576 # 1 Mb en b
            resultado.append((RestriccionesSonido.MUY_PESADO,
                              (f"El archivo pesa `{round(tags.filesize / mb, 3)} MB`, debería " +
                              f"ser como máximo `{TAMANIO_MAXIMO_AUDIO} MB`")))

        if tags.duration > DURACION_MAXIMA_AUDIO: # No más de 8 seg
            resultado.append((RestriccionesSonido.DEMASIADO_LARGO,
                              (f"El audio dura `{round(tags.duration, 3)} segundos`. Se permite " +
                               f"que sea como máximo de `{DURACION_MAXIMA_AUDIO} segundos`")))

        return resultado


    @appcommand(name="quitar",
                description="Elimina un sonido asignado a un usuario.")
    @describe(sonido="El sonido a quitar.",
              usuario="El usuario al que quitarle el sonido.")
    @autocomplete(usuario=autocompletado_miembros_guild)
    async def quitar_sonido(self,
                            interaccion: Interaction,
                            sonido: str,
                            usuario: Optional[str]=None) -> None:
        """
        Elimina un sonido asignado a un usuario.
        """

        autor = interaccion.user

        if usuario is not None and not self.bot.es_admin(autor.id):
            await interaccion.response.send_message(content=f"{autor.mention}, señor, usted no " +
                                                     "tiene permiso para eliminar los sonidos " +
                                                     "de los demás.",
                                                    ephemeral=True)
            return

        if usuario is None:
            usuario: "Member" = autor
        else:
            usuario: "Member" = interaccion.guild.get_member(int(usuario))


class CogAudio(_CogABC):
    """
    Cog para comandos de audio.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoAudio, GrupoSonido]


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

        reconexion = "reconecté" if es_mismo_canal else "conecté"
        await interaccion.response.send_message(content=f"Ya me {reconexion}!",
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
            await interaccion.response.send_message(content=("No estoy conectado a ningún " +
                                                             "canal de voz."),
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
