"""
Módulo para preguntar al usuario si quiere borrar el directorio.
"""

from typing import Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View, button

from ..archivos import borrar_dir, partir_ruta


class ConfirmacionDestruir(View):
    """
    Clase para pedir confirmación de si borrar el directorio seleccionado o no.
    """

    def __init__(self, ruta: str, timeout: Optional[float]=120.0) -> None:
        """
        Inicializa una instancia de 'ConfirmacionDestruir'.
        """
        super().__init__(timeout=timeout)
        self.dir = ruta


    @button(label="Que siiiiiiiii",
            style=ButtonStyle.red,
            custom_id="destroy",
            emoji=Emoji.from_str("<:pprage:851967647679250493>"))
    async def confirmar_destruir(self, _boton: Button, interaction: Interaction) -> None:
        """
        Confirma que se quiere destruir un directorio.
        """
        borrar_dir(self.dir)
        nombre = partir_ruta(self.dir)[1]
        await interaction.message.edit(content=f'*Carpeta `{nombre}` borrada con éxito*',
                                       view=None,
                                       delete_after=5.0)


    @button(label="Mejor no...",
            style=ButtonStyle.grey,
            custom_id="cancel_del",
            emoji=Emoji.from_str("<:pepetowel:945157841751253082>"))
    async def cancelar_guardar(self, _boton: Button, interaction: Interaction) -> None:
        """
        Cancela la destrucción.
        """
        await interaction.message.edit(content='Bueno, entonces...', view=None, delete_after=3.0)
