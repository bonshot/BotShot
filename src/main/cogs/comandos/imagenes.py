"""
Cog para manejar imágenes.
"""

from typing import TYPE_CHECKING

from discord import File, Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe

from ...archivos import archivo_random
from ...db.atajos import get_imagenes_path
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogImagenes(_CogABC):
    """
    Cog para comandos de manejar imágenes.
    """

    @appcommand(name='randart',
                description='Muestra una imagen aleatoria.')
    @describe(cantidad="La cantidad de imágenes a mandar. Máximo 15 (quince).")
    async def gimmerandart(self, interaccion: Interaction, cantidad: int=1) -> None:
        """|
        Mandar una foto random.
        """
        path_archivo = get_imagenes_path()
        limite = 15
        cantidad = (cantidad if cantidad > 0 else 1)

        if cantidad > limite:
            await interaccion.response.send_message(content=f'¡Pará {interaccion.user.mention}, marrano! ' +
                                                             'No puedo con tantas imágenes, el límite ' +
                                                             f'es `{limite}`.')
        else:
            await interaccion.response.send_message(content='Disfruta de tu porno, puerco de mierda ' +
                                                             f'{interaccion.user.mention}')

        arch = File(archivo_random(path_archivo))
        await interaccion.channel.send(content=f'**||{arch.filename}||**',
                                        file=arch)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogImagenes(bot))
