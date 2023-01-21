"""
Cog de comandos para hacer pruebas.
"""

from io import BytesIO
from math import sqrt
from typing import TYPE_CHECKING

from discord import File, Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from PIL.Image import new as img_new
from PIL.Image import open as img_open
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

from ...db.atajos import get_img_juegos_path, get_minecraftia_font
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from ...botshot import BotShot


class CogPruebas(_CogABC):
    """
    Cog para comandos de pruebas.
    """

    @appcommand(name='suma',
                description='Suma dos números enteros.')
    @describe(x="Primer número a sumar.",
              y="Segundo número a sumar.")
    async def suma(self, interaccion: Interaction, x: int, y: int) -> None:
        """
        Suma dos enteros y envía por el canal el resultado.
        """

        await interaccion.response.send_message(f'{x} + {y} = {x + y}')

    @appcommand(name="fib",
                description="Devuelve el elemento de psoición 'n' en la sucesión " +
                            "de fibonacci, en tiempo constante.")
    @describe(n="La posición del número a devolver.")
    async def fib(self, interaccion: Interaction, n: int) -> None:
        """
        Devuelve un número en la posición 'n' en la sucesión
        de fibonacci.
        """

        res = int((((1 + sqrt(5)) ** n) - ((1 - sqrt(5)) ** n)) / ((2 ** n) * sqrt(5)))
        await interaccion.response.send_message(f"Fib(**{n}**)  =  **{res}**")


    @appcommand(name="img",
                description="[TEMP] Comando temporal para jugar con imágenes de Pillow.")
    async def img_create(self, interaccion: Interaction) -> None:
        "Juega con imágenes."

        dix, diy = 15, 5
        dx, dy = 20, 10
        diam = 70

        with img_open(f"{get_img_juegos_path()}/4_en_linea/4_en_linea_tablero.png",
                      formats=("png",)) as im:
            x, y = im.size
            img = img_new("RGBA", (x, y + diy+3*dy))
            img.paste(im.copy())

        d = Draw(img)
        d.rectangle((0, y + diy, x, y + diy+3*dy),
                    fill="#3c7de6")
        for i in range(7):
            tx = dix + i * (dx + diam) + diam // 2
            d.text((tx, y + diy + 1.5 * dy), f"{i + 1}",
                   font=truetype(get_minecraftia_font(), 20),
                   fill="#ffffff",
                   anchor="mm")
            
            lx = (dix if i > 0 else 0) + i * (dx + diam) - dx // 2
            d.line((lx, y + diy, lx, y + diy+3*dy),
                    fill="#2e6ac9", width=4)


        arch = BytesIO()
        img.save(arch, "PNG")
        arch.seek(0) # Necesario pues guardarlo deja el cursor al final del buffer
        await interaccion.response.send_message(content="*Mostrando imagen de prueba...*",
                                                file=File(fp=arch, filename="prueba.png"),
                                                ephemeral=True)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogPruebas(bot))
