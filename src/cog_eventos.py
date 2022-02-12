"""
Cog para el handler de navegador de carpetas.
"""

from discord import Message, Guild
from discord.ext.commands import Cog, Context

from categoria_comandos import CategoriaComandos
from logger import log
from checks import es_canal_escuchado, mensaje_tiene_imagen
from archivos import cargar_json, guardar_json
from confirmacion_guardar import ConfirmacionGuardar
from constantes import DEFAULT_PREFIX, PROPERTIES_FILE

class CogEventos(CategoriaComandos):
    """
    Cog para confirmar si guardar imágenes.
    """

    @Cog.listener()
    async def on_ready(self) -> None:
        """
        El bot se conectó y está listo para usarse.
        """
        log.info(f'¡{self.bot.user} conectado y listo para utilizarse!')

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        """
        El bot se conectó por primera vez a un servidor.
        """

        log.info(f'El bot se conectó a "{guild.name}"')

        dic_propiedades = cargar_json(PROPERTIES_FILE)
        dic_propiedades['prefijos'][str(guild.id)] = DEFAULT_PREFIX

        guardar_json(dic_propiedades, PROPERTIES_FILE)

    @Cog.listener()
    async def on_message(self, mensaje: Message) -> None:
        """
        Escucha un mensaje enviado si este tiene una imagen.
        """
        if any((mensaje.author == self.bot.user,
            not es_canal_escuchado(mensaje),
            not mensaje_tiene_imagen(mensaje))):
            return

        log.info(f"EL usuario {mensaje.author} ha enviado una imagen al canal '{mensaje.channel.name}' del server '{mensaje.guild.name}' mediante {'un mensaje sin contenido' if not mensaje.content else f'el mensaje `{mensaje.content}`'}")
        await mensaje.channel.send(content="¿Querés guardarlo pibe?", view=ConfirmacionGuardar(), delete_after=120, reference=mensaje.to_reference())

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        """
        Escucha si se escribió un comando.
        """
        log.info(f"El usuario {ctx.author} está tratando de invocar '{ctx.command}' en el canal '#{ctx.channel.name}' del server '{ctx.guild.name}' mediante el mensaje '{ctx.message.content}'")

    @Cog.listener()
    async def on_command_completion(self, ctx: Context) -> None:
        """
        Escucha si se completó el comando escrito.
        """
        log.info(f"{ctx.author} ha invocado '{ctx.command}' satisfactoriamente")