"""
Módulo para preguntar al usuario si quiere guardar una imagen.
"""

from typing import Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View, button

from ...db.atajos import get_imagenes_path
from .selector_carpetas import SelectorCarpeta


class ConfirmacionGuardar(View):
    """
    Clase para pedir confirmación de si guardar una imagen o no.
    """

    def __init__(self, timeout: Optional[float]=120.0) -> None:
        """
        Inicializa una instancia de 'ConfirmacionGuardar'.
        """
        super().__init__(timeout=timeout)


    @button(label="Obvio",
            style=ButtonStyle.green,
            custom_id="confirm",
            emoji=Emoji.from_str("\U00002705"))
    async def confirmar_guardar(self, interaction: Interaction, _boton: Button) -> None:
        """
        Confirma que se quiere guardar algo.
        """
        await interaction.response.edit_message(content=f'Guardando en `{get_imagenes_path()}`',
                                                view=SelectorCarpeta())


    @button(label="Nah",
            style=ButtonStyle.red,
            custom_id="cancel",
            emoji=Emoji.from_str("\U0000274C"))
    async def cancelar_guardar(self, interaction: Interaction, _boton: Button) -> None:
        """
        Cancela la guardación.
        """
        await interaction.response.edit_message(content='Bueno, chau.',
                                                view=None)
