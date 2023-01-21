"""
Cog para manejar imágenes.
"""

from typing import TYPE_CHECKING, Optional

from discord import File, Interaction
from discord.app_commands import Choice, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe

from ...archivos import archivo_random
from ...db.atajos import get_imagenes_path, get_limite_randart
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogImagenes(_CogABC):
    """
    Cog para comandos de manejar imágenes.
    """

    @appcommand(name='randart',
                description='Muestra una imagen aleatoria.')
    @describe(cantidad=f"La cantidad de imágenes a mandar. Como máximo {get_limite_randart()}.",
              es_spoiler="Si las imágenes deben venir ocultas. Por defecto no es así.",
              ruta_absoluta="Si utilizar una ruta local (debe ser absoluta).")
    @choices(es_spoiler=[
        Choice(name="No", value=0),
        Choice(name="Sí", value=1)
    ])
    async def gimmerandart(self,
                           interaccion: Interaction,
                           cantidad: int=1,
                           es_spoiler: Choice[int]=0,
                           ruta_absoluta: Optional[str]=None) -> None:
        """
        Mandar una foto random.
        """
        path_archivo = (get_imagenes_path() if ruta_absoluta is None else rf"{ruta_absoluta}")
        limite = get_limite_randart()
        cantidad = (cantidad if cantidad > 0 else 1)

        if cantidad > limite:
            await interaccion.response.send_message(
                    content=f'¡Pará {interaccion.user.mention}, marrano! No puedo con tantas ' +
                    f'imágenes, el límite es `{limite}`.'
            )
            cantidad = limite
        else:
            await interaccion.response.send_message(content='Disfruta de tu porno, puerco de mierda ' +
                                                             f'{interaccion.user.mention}')

        for _ in range(cantidad):
            arch = File(archivo_random(path_archivo,
                                       incluir_subcarpetas=True),
                        spoiler=bool(es_spoiler))
            await interaccion.channel.send(content=f'**||{arch.filename}||**',
                                        file=arch)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogImagenes(bot))
