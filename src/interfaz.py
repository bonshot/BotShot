"""
Módulo para contener la interfaz de algunos mensajes.
"""

from constantes import IMAGES_PATH
from archivos import lista_carpetas, unir_ruta
from typing import Optional
from discord import Interaction, SelectOption,PartialEmoji as Emoji
from discord.ui import View, Select, Button, button
from discord.enums import ButtonStyle

class ConfirmacionGuardar(View):
    """
    Clase para pedir confirmación de si guardar una imagen o no.
    """

    def __init__(self, timeout: Optional[float]=120.0) -> None:
        """
        Crea una instancia de 'ConfirmacionGuardar'.
        """
        super().__init__(timeout=timeout)
        
    @button(label="Obvio", style=ButtonStyle.green, custom_id="confirm", emoji=Emoji.from_str("<:rule34:891890132737736734>"))
    async def confirmarGuardar(self, boton: Button, interaccion: Interaction) -> None:
        """
        Confirma que se quiera guardar algo.
        """
        await interaccion.message.edit(view=SelectorCarpeta(IMAGES_PATH))

    @button(label="Nah", style=ButtonStyle.red, custom_id="cancel", emoji=Emoji.from_str("<:pepeoi:889008419242119219>"))
    async def cancelarGuardar(self, boton: Button, interaccion: Interaction) -> None:
        """
        Cancela la guardación.
        """
        await interaccion.message.edit(content="Bueno, chau.", view=None)
        await interaccion.message.delete(delay=3)


class MenuCarpetas(Select):
    """
    Clase para el menú con el que seleccionar carpetas.
    """

    def __init__(
        self,
        *,
        ruta: str,
        lista_rutas: list[str],
        custom_id: str="menu_selector_carpetas",
        placeholder: Optional[str]="Seleccione una Carpeta",
        min_values: int=1,
        max_values: int=1,
        disabled: bool=False,
        row: Optional[int]=None
    ) -> None:
        """
        Crea una instancia de 'MenuCarpetas'.
        """
        self.path = ruta
        opciones = [SelectOption(label=' '.join(carpeta.split('_')), value=carpeta) for carpeta in lista_rutas]

        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=opciones, disabled=disabled, row=row)

    async def callback(self, interaccion: Interaction) -> None:
        """
        Procesa la opción elegida.
        """
        eleccion = self.values[0]
        self.path = unir_ruta(self.path, eleccion)
        carpetas_actuales = lista_carpetas(self.path)

        if carpetas_actuales:
            await interaccion.message.edit(view=SelectorCarpeta(self.path))
            return

        mensaje_referido = interaccion.message.reference
        if mensaje_referido:
            mensaje = await interaccion.channel.fetch_message(mensaje_referido.message_id)
            if mensaje.attachments:
                imagen = mensaje.attachments[0]
                await imagen.save(unir_ruta(self.path, imagen.filename))
                await interaccion.message.edit(content=f"Guardado en `{self.path}`, Goshujin-Sama <:ouiea:862131679073927229>", view=None, delete_after=10)

class SelectorCarpeta(View):
    """
    Clase para seleccionar la carpeta en donde guardar la imagen.
    """

    def __init__(self, ruta: str, timeout: Optional[float]=120.0) -> None:
        """
        Crea una instancia de 'SelectorCarpeta'.
        """
        super().__init__(timeout=timeout)
        carpetas = lista_carpetas(ruta)

        self.add_item(MenuCarpetas(ruta=ruta, lista_rutas=carpetas))

