"""
Módulo para explorar y borrar una carpeta.
"""

from typing import Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from ..archivos import lista_carpetas, partir_ruta, unir_ruta
from ..db.atajos import get_imagenes_path
from .confirmacion_destruir import ConfirmacionDestruir
from .selector_carpetas import MenuCarpetas, SelectorCarpeta


class MenuDestructorCarpetas(MenuCarpetas):
    """
    Clase de menú para crear carpetas.
    """

    def __init__(
        self,
        *,
        ruta: str,
        lista_rutas: list[str],
        custom_id: str="menu_destructor_carpetas",
        placeholder: Optional[str]="Seleccione una Carpeta",
        min_values: int=1,
        max_values: int=1,
        disabled: bool=False,
        row: Optional[int]=1
    ) -> None:
        """
        Inicializa una instancia de 'MenuDestructorCarpetas'.
        """

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

        await interaction.response.edit_message(content=f"Actualmente en `{self.path}`",
                                                view=DestructorCarpetas(self.path))
        return True


class DestructorCarpetas(SelectorCarpeta):
    """
    Clase para crear carpetas y/o directorios.
    """

    @property
    def mensaje_refrescar(self) -> str:
        """
        El string que se muestra al refrescar el mensaje.
        """

        return f"Actualmente en `{self.ruta}`"


    def generar_menu(self) -> MenuDestructorCarpetas:
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

        return MenuDestructorCarpetas(ruta=self.ruta,
                                      lista_rutas=ls_rutas,
                                      placeholder=placeholder)


    @button(label="Borrar Directorio",
            style=ButtonStyle.red,
            custom_id="del_dir",
            row=2,
            emoji=Emoji.from_str("\U0000274C"))
    async def borrar_carpeta(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Pregunta si se desea borrar la carpeta deseada.
        """

        ruta_raiz = get_imagenes_path()

        if self.ruta == ruta_raiz:
            msg = "\n\n*...estas...*\n*...estás tratando de borrar la carpeta raíz!?*"
            await interaccion.response.edit_message(content=msg,
                                                    view=self)
            return

        await interaccion.response.edit_message(content="¿Estás ***seguro*** de que querés borrar " +
                                                        f"`{partir_ruta(self.ruta)[1]}`?",
                                                view=ConfirmacionDestruir(ruta=self.ruta))
