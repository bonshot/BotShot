"""
Cog que agrupa comandos para manejar directorios.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.ext.commands import Context

from ...archivos import unir_ruta
from ...db.atajos import existe_usuario_autorizado, get_imagenes_path
from ...interfaces import CreadorCarpetas, DestructorCarpetas
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogDirs(_CogABC):
    """
    Cog para comandos de directorios.
    """

    def cog_check(self, ctx: Context) -> bool:
        """
        Verifica si el que invoca el comando es un admin o un dev.
        """

        return ((ctx.author.id == self.bot.owner_id)
                 or existe_usuario_autorizado(ctx.author.id))


    @appcommand(name='mkdir',
                description='[ADMIN] Crea una nueva carpeta.')
    @describe(nombre="El nombre de la carpeta a crear.")
    async def crear_carpeta(self, interaction: Interaction, nombre: str) -> None:
        """
        Crea una nueva carpeta en un directorio a elección.
        """
        nombre = '_'.join(nombre.split())
        await interaction.channel.send(f"Creando como `{unir_ruta(get_imagenes_path(), nombre)}`",
                                       view=CreadorCarpetas(nombre_carpeta=nombre),
                                       delete_after=30.0)
        await interaction.response.send_message("¡Creando carpeta!",
                                                ephemeral=True)


    @appcommand(name='rmdir',
                description='[ADMIN] Borra una carpeta.')
    async def borrar_carpeta(self, interaction: Interaction) -> None:
        """
        Explora las carpetas, con posibilidad de borrar un directorio.
        """
        await interaction.channel.send(f'Actualmente en `{get_imagenes_path()}`',
                                       view=DestructorCarpetas(),
                                       delete_after=30.0)
        await interaction.response.send_message("¡Destruyendo carpeta!",
                                                ephemeral=True)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogDirs(bot))
