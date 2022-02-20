"""
Cog para manejar imágenes.
"""

from discord import File
from discord.ext.commands import Context, command

from ..archivos import archivo_random, carpeta_random, tiene_subcarpetas
from ..constantes import IMAGES_PATH
from .categoria_comandos import CategoriaComandos


class CogImagenes(CategoriaComandos):
    """
    Cog para comandos de manejar imágenes.
    """

    @command(name='randart',
             help='Manda una foto random')
    async def gimmerandart(self, ctx: Context) -> None:
        """|
        Mandar una foto random.
        """
        path_archivo = IMAGES_PATH

        while tiene_subcarpetas(path_archivo):
            path_archivo = carpeta_random(path_archivo)
        foto_random = File(archivo_random(path_archivo))

        await ctx.channel.send(content='Disfruta de tu porno, puerco de mierda ' +
                                       f'{ctx.author.mention}',
                               file=foto_random)
