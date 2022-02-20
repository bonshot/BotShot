"""
Cog que agrupa comandos administrativos.
"""

from discord import has_role
from discord.ext.commands import command, Context

from .categoria_comandos import CategoriaComandos
from ..archivos import cargar_json, guardar_json
from ..constantes import DEV_ROLE_ID, PROPERTIES_FILE


class CogAdmin(CategoriaComandos):
    """
    Cog para comandos administrativos.
    """

    @command(name='prefix',
             aliases=['prefijo', 'pfx', 'px'],
             help='[ADMIN] Cambia el prefijo de los comandos.')
    async def cambiar_prefijo(self, ctx: Context, nuevo_prefijo: str) -> None:
        """
        Cambia el prefijo utilizado para convocar a los comandos, solamente del
        servidor de donde el comando fue escrito.

        Se da por hecho que el servidor ya está memorizado en el diccionario.
        """

        prefijo_viejo = ctx.prefix

        if prefijo_viejo == nuevo_prefijo:

            await ctx.channel.send(f'Cariño, `{nuevo_prefijo}` *ya es* el prefijo ' +
                                    'para este server.',
                                   delete_after=10)
            return

        dic_propiedades = cargar_json(PROPERTIES_FILE)
        dic_propiedades['prefijos'][str(ctx.guild.id)] = nuevo_prefijo
        guardar_json(dic_propiedades, PROPERTIES_FILE)

        await ctx.channel.send('**[AVISO]** El prefijo de los comandos fue cambiado de ' +
                               f'`{prefijo_viejo}` a `{nuevo_prefijo}` exitosamente.',
                               delete_after=30)


    @command(name='shutdown',
             aliases=['apagar'],
             help='[ADMIN] Apaga el Bot.',
             hidden=True)
    @has_role(DEV_ROLE_ID)
    async def apagar_bot(self, ctx: Context) -> None:
        """
        Cierra el Bot de manera correcta.
        """
        self.bot.log.info("¡Cerrando el Bot!")
        await ctx.message.delete()
        await self.bot.close()
