"""
Cog que agrupa comandos administrativos.
"""

from typing import TYPE_CHECKING

from discord.ext.commands import Context, command

from ..archivos import cargar_json, guardar_json, unir_ruta
from ..constantes import DEV_ROLE_ID, IMAGES_PATH, PROPERTIES_FILE
from ..interfaces import CreadorCarpetas, DestructorCarpetas
from .categoria_comandos import CategoriaComandos

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogAdmin(CategoriaComandos):
    """
    Cog para comandos administrativos.
    """

    def cog_check(self, ctx: Context) -> bool:
        """
        Verifica si el que invoca el comando es un admin o un dev.
        """

        try:
            return ctx.author.get_role(DEV_ROLE_ID)
        except AttributeError:
            return False


    async def cog_after_invoke(self, ctx: Context) -> None:
        """
        Borra los mensajes de admin después de un tiempo ejecutado
        el comando.
        """
        await ctx.message.delete(delay=5.0)


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
    async def apagar_bot(self, ctx: Context) -> None:
        """
        Cierra el Bot de manera correcta.
        """
        self.bot.log.info("¡Cerrando el Bot!")
        await ctx.message.delete()
        await self.bot.close()


    @command(name='mkdir',
             aliases=['addfd', 'nuevacarpeta'],
             help='[ADMIN] Crea una nueva carpeta.')
    async def crear_carpeta(self, ctx: Context, *nombre) -> None:
        """
        Crea una nueva carpeta en un directorio a elección.
        """
        if not nombre:
            await ctx.channel.send("**[ERROR]** Nombre de carpeta vacío.", delete_after=10.0)
            self.bot.log.error("Nombre de carpeta no válido (nombre vacío)")
            return

        nombre = '_'.join(nombre)
        await ctx.channel.send(f"Creando como `{unir_ruta(IMAGES_PATH, nombre)}`",
                               view=CreadorCarpetas(nombre_carpeta=nombre),
                               delete_after=120.0)


    @command(name='rmdir',
             aliases=['delfd', 'borrarcarpeta'],
             help='[ADMIN] Borra una carpeta.')
    async def borrar_carpeta(self, ctx: Context) -> None:
        """
        Explora las carpetas, con posibilidad de borrar un directorio.
        """

        await ctx.channel.send(f'Actualmente en `{IMAGES_PATH}`',
                               view=DestructorCarpetas(),
                               delete_after=120.0)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogAdmin(bot))
