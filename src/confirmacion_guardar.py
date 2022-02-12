"""
Módulo para preguntar al usuario si quiere guardar una imagen.
"""

from constantes import IMAGES_PATH
from typing import Optional
from discord import Interaction, PartialEmoji as Emoji
from discord.ui import View, Button, button
from discord.enums import ButtonStyle
from selector_carpetas import SelectorCarpeta

class ConfirmacionGuardar(View):
    """
    Clase para pedir confirmación de si guardar una imagen o no.
    """

    def __init__(self, timeout: Optional[float]=120.0) -> None:
        """
        Inicializa una instancia de 'ConfirmacionGuardar'.
        """
        super().__init__(timeout=timeout)
        
    @button(label="Obvio", style=ButtonStyle.green, custom_id="confirm", emoji=Emoji.from_str("<:rule34:891890132737736734>"))
    async def confirmarGuardar(self, _boton: Button, interaccion: Interaction) -> None:
        """
        Confirma que se quiera guardar algo.
        """
        await interaccion.message.edit(content=f"Guardando en `{IMAGES_PATH}`", view=SelectorCarpeta())

    @button(label="Nah", style=ButtonStyle.red, custom_id="cancel", emoji=Emoji.from_str("<:pepeoi:889008419242119219>"))
    async def cancelarGuardar(self, _boton: Button, interaccion: Interaction) -> None:
        """
        Cancela la guardación.
        """
        await interaccion.message.edit(content="Bueno, chau.", view=None)
        await interaccion.message.delete(delay=3)
