"""
Módulo para explorar y crear una carpeta.
"""

from typing import Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from ..archivos import crear_dir, lista_carpetas, partir_ruta, unir_ruta
from ..constantes import IMAGES_PATH
from .selector_carpetas import MenuCarpetas, SelectorCarpeta


class MenuCreadorCarpetas(MenuCarpetas):
    """
    Clase de menú para crear carpetas.
    """

    def __init__(
        self,
        *,
        nombre_carpeta: str,
        ruta: str,
        lista_rutas: list[str],
        custom_id: str="menu_creador_carpetas",
        placeholder: Optional[str]="Seleccione una Carpeta",
        min_values: int=1,
        max_values: int=1,
        disabled: bool=False,
        row: Optional[int]=1
    ) -> None:
        """
        Inicializa una instancia de 'MenuCreadorCarpetas'.
        """

        self.nombre = nombre_carpeta

        super().__init__(ruta=ruta,
                         lista_rutas=lista_rutas,
                         custom_id=custom_id,
                         placeholder=placeholder,
                         min_values=min_values,
                         max_values=max_values,
                         disabled=disabled,
                         row=row)


    async def callback(self, interaction: Interaction) -> None:
        """
        Procesa la opción elegida.
        """
        eleccion = self.values[0]
        if lista_carpetas(self.path):
            self.path = unir_ruta(self.path, eleccion)
        carpetas_siguientes = lista_carpetas(self.path)

        if await self.seguir(carpetas_siguientes, interaction):
            return


    async def seguir(self, _carpetas: list[str], interaction: Interaction) -> bool:
        """
        Cambia la vista por otra, y sigue navegando.
        """

        await interaction.response.edit_message(content="Creando como " +
                                                        f"`{unir_ruta(self.path, self.nombre)}`",
                                                view=CreadorCarpetas(self.nombre, self.path))
        return True


class CreadorCarpetas(SelectorCarpeta):
    """
    Clase para crear carpetas y/o directorios.
    """

    def __init__(self,
                 nombre_carpeta: str,
                 ruta: str=IMAGES_PATH,
                 pagina: int=0,
                 timeout: Optional[float]=120.0) -> None:
        """
        Inicializa una instancia de 'CreadorCarpeta'.
        """

        self.nombre: str = nombre_carpeta
        super().__init__(ruta, pagina, timeout)


    @property
    def mensaje_refrescar(self) -> str:
        """
        El string que se muestra al refrescar el mensaje.
        """

        return f"Creando como `{unir_ruta(self.ruta, self.nombre)}`"


    def generar_menu(self) -> MenuCreadorCarpetas:
        """
        Genera un nuevo menú de carpetas.
        """


        if self.cantidad_elementos:
            desde = self.pagina * self.cantidad_elementos
            hasta = (self.pagina + 1) * self.cantidad_elementos

            ls_rutas = self.carpetas[desde:hasta]
            placeholder = "Seleccione un directorio"
        else:
            ls_rutas = [partir_ruta(self.ruta)[1]]
            placeholder = "No hay carpetas..."

        return MenuCreadorCarpetas(nombre_carpeta=self.nombre,
                                   ruta=self.ruta,
                                   lista_rutas=ls_rutas,
                                   placeholder=placeholder)


    @button(label="Crear",
            style=ButtonStyle.grey,
            custom_id="new_dir",
            row=2,
            emoji=Emoji.from_str("\U00002705"))
    async def crear_carpeta(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Crea definitivamente la carpeta deseada.
        """

        if self.nombre in self.carpetas:
            msg = (interaccion.message.content + "\n\nMe da que no, capo. " +
                   f"El nombre `{self.nombre}` está repetido y ya está creado.")
            await interaccion.response.edit_message(content=msg,
                                                    view=self)
            return

        ruta_definitiva = unir_ruta(self.ruta, self.nombre)
        crear_dir(ruta_definitiva)
        await interaccion.response.edit_message(content=f"Directorio `{ruta_definitiva}` creado, pa.",
                                                view=None)
