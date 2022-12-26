"""
Cog para el handler de navegador de carpetas.
"""

from typing import TYPE_CHECKING

from discord import Guild, Message
from discord.ext.commands import Cog, Context

from ..checks import es_canal_escuchado, mensaje_tiene_imagen
from ..db.atajos import actualizar_guild
from ..interfaces import ConfirmacionGuardar
from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogEventos(_CogABC):
    """
    Cog para confirmar si guardar imágenes.
    """

    @Cog.listener()
    async def on_ready(self) -> None:
        """
        El bot se conectó y está listo para usarse.
        """
        self.bot.log.info("Actualizando base de datos...")
        self.bot.actualizar_db()

        self.bot.log.info(f'¡{self.bot.user} conectado y listo para utilizarse!')


    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        """
        El bot se conectó por primera vez a un servidor.
        """

        self.bot.log.info(f'El bot se conectó a "{guild.name}"')
        actualizar_guild(guild.id, guild.name)


    @Cog.listener()
    async def on_message(self, mensaje: Message) -> None:
        """
        Escucha un mensaje enviado si este tiene una imagen.
        """
        if any((
            mensaje.author == self.bot.user,
            not es_canal_escuchado(mensaje),
            not mensaje_tiene_imagen(mensaje))):
            return

        self.bot.log.info(f'EL usuario {mensaje.author} ha enviado una imagen al canal ' +
                          f'"{mensaje.channel.name}" del server "{mensaje.guild.name}" ' +
                          f'mediante {"un mensaje sin contenido" if not mensaje.content else f"el mensaje `{mensaje.content}`"}') #pylint: disable=line-too-long
        await mensaje.channel.send(content='¿Querés guardarlo pibe?',
                                   view=ConfirmacionGuardar(),
                                   delete_after=30,
                                   reference=mensaje.to_reference())


    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        """
        Escucha si se escribió un comando.
        """
        self.bot.log.info(f'El usuario {ctx.author} está tratando de invocar "{ctx.command}" ' +
                          f'en el canal "#{ctx.channel.name}" del server ' +
                          f'"{ctx.guild.name}" mediante el mensaje "{ctx.message.content}"')


    @Cog.listener()
    async def on_command_completion(self, ctx: Context) -> None:
        """
        Escucha si se completó el comando escrito.
        """
        self.bot.log.info(f'{ctx.author} ha invocado "{ctx.command}" satisfactoriamente')


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogEventos(bot))
