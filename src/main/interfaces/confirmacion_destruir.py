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
            emoji=Emoji.from_str("<:peperage:851967647679250493>"))
    async def confirmar_destruir(self, interaction: Interaction, _boton: Button) -> None:
        """
        Confirma que se quiere destruir un directorio.
        """
        borrar_dir(self.dir)
        nombre = partir_ruta(self.dir)[1]
        await interaction.response.edit_message(content=f'*Carpeta `{nombre}` borrada con éxito*',
                                                view=None)


    @button(label="Mejor no...",
            style=ButtonStyle.grey,
            custom_id="cancel_del",
            emoji=Emoji.from_str("<:worrytowel:846950118385254442>"))
    async def cancelar_guardar(self, interaction: Interaction, _boton: Button) -> None:
        """
        Cancela la destrucción.
        """
        await interaction.response.edit_message(content='Bueno, entonces...',
                                                view=None)
