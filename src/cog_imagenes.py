"""
Cog para manejar imágenes.
"""

from discord import File
from discord.ext.commands import command, Context

from categoria_comandos import CategoriaComandos
from archivos import tiene_subcarpetas, carpeta_random, archivo_random
from constantes import IMAGES_PATH

class CogImagenes(CategoriaComandos):
    """
    Cog para comandos de manejar imágenes.
    """

    @command(name='randart', help='Manda una foto random')
    async def gimmerandart(self, ctx: Context) -> None:
        """|
        Mandar una foto random.
        """
        path_archivo = IMAGES_PATH

        while tiene_subcarpetas(path_archivo):
            path_archivo = carpeta_random(path_archivo)
        foto_random = File(archivo_random(path_archivo))

        await ctx.channel.send(content=f"Disfruta de tu porno, puerco de mierda {ctx.author.mention}", file=foto_random)
