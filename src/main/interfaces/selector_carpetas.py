"""
Módulo para seleccionar una carpeta.
"""

from typing import Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord import SelectOption
from discord.enums import ButtonStyle
from discord.ui import Button, Select, View, button

from ..archivos import lista_carpetas, partir_ruta, unir_ruta
from ..constantes import IMAGES_PATH


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
        row: Optional[int]=1
    ) -> None:
        """
        Inicializa una instancia de 'MenuCarpetas'.
        """
        self.path = ruta

        opciones = [SelectOption(label=' '.join(carpeta.split('_')), value=carpeta)
                                 for carpeta in lista_rutas]

        super().__init__(custom_id=custom_id,
                         placeholder=placeholder,
                         min_values=min_values,
                         max_values=max_values,
                         options=opciones,
                         disabled=disabled,
                         row=row)


    async def callback(self, interaction: Interaction) -> None:
        """
        Procesa la opción elegida.
        """
        eleccion = self.values[0]
        self.path = unir_ruta(self.path, eleccion)
        carpetas_actuales = lista_carpetas(self.path)

        if await self.seguir(carpetas_actuales, interaction):
            return

        await self.guardar_img(interaction)


    async def seguir(self, carpetas: list[str], interaction: Interaction) -> bool:
        """
        Cambia la vista por otra, y sigue navegando.
        """

        if carpetas:
            await interaction.message.edit(content=f'Guardando en `{self.path}`',
                                           view=SelectorCarpeta(self.path))
            return True
        return False


    async def guardar_img(self, interaction: Interaction) -> None:
        """
        Deja de navegar y guarda la imagen especificada.
        """

        mensaje_referido = interaction.message.reference
        if mensaje_referido:
            mensaje = await interaction.channel.fetch_message(mensaje_referido.message_id)
            if mensaje.attachments:
                imagen = mensaje.attachments[0]
                await imagen.save(unir_ruta(self.path, imagen.filename))
                await interaction.message.edit(content=f'Guardado en `{self.path}`, ' +
                                                        'Goshujin-Sama <:ouiea:862131679073927229>',
                                               view=None,
                                               delete_after=10)


class SelectorCarpeta(View):
    """
    Clase para seleccionar la carpeta en donde guardar la imagen.
    """

    def __init__(self,
                 ruta: str=IMAGES_PATH,
                 pagina: int=0,
                 timeout: Optional[float]=120.0) -> None:
        """
        Inicializa una instancia de 'SelectorCarpeta'.
        """
        super().__init__(timeout=timeout)
        self.ruta: str = ruta
        self.pagina: int = pagina

        self.menu_carpetas: Optional[MenuCarpetas] = None
        self.refrescar_menu()


    @property
    def cantidad_elementos(self) -> int:
        """
        Devuelve la cantidad de elementos disponible en la pagina.
        """

        max_elementos: int = 20

        return (max_elementos
                if self.cantidad_rutas > max_elementos
                else self.cantidad_rutas)


    @property
    def carpetas(self) -> MenuCarpetas:
        """
        Calcula las carpetas que hay en la ruta actual.
        """
        return lista_carpetas(self.ruta)


    @property
    def cantidad_rutas(self) -> int:
        """
        Devuelve la cantidad de rutas disponibles.
        """
        return len(self.carpetas)


    @property
    def max_paginas(self) -> int:
        """
        Devuelve el límite de páginas a obedecer.
        Esto se usa para bloquear botones de ser necesario.
        """

        if not self.cantidad_elementos:
            return 0

        return ((self.cantidad_rutas // self.cantidad_elementos) +
                (1 if self.cantidad_rutas % self.cantidad_elementos else 0))


    def generar_menu(self) -> MenuCarpetas:
        """
        Genera un nuevo menú de carpetas.
        """
        desde = self.pagina * self.cantidad_elementos
        hasta = (self.pagina + 1) * self.cantidad_elementos

        return MenuCarpetas(ruta=self.ruta, lista_rutas=self.carpetas[desde:hasta])


    def refrescar_menu(self) -> None:
        """
        Agrega el menú a la vista, y elimina el anterior, si había uno.
        """
        self.remove_item(self.menu_carpetas)
        self.menu_carpetas = self.generar_menu()
        self.add_item(self.menu_carpetas)
        self.actualizar_botones()


    async def refrescar_mensaje(self, interaccion: Interaction) -> None:
        """
        Refresca el mensaje con la vista nueva.
        """
        await interaccion.message.edit(content=f'Guardando en `{self.ruta}`',
                                       view=self)


    def actualizar_boton(self, boton: Button) -> None:
        """
        Oculta el botón dependiendo de la página actual.
        """

        boton.disabled = any(((boton.custom_id == "go_back" and self.ruta == IMAGES_PATH),
                            (boton.custom_id == "pg_back" and self.pagina <= 0),
                            (boton.custom_id == "pg_next" and self.pagina >= (self.max_paginas - 1))
                             ))


    def actualizar_botones(self) -> None:
        """
        Desactiva los botones o no dependiendo en
        la página donde se está parado.
        """
        for item in self.children:
            if isinstance(item, Button):
                self.actualizar_boton(item)


    @button(label="Volver",
            style=ButtonStyle.gray,
            custom_id="go_back",
            row=2,
            emoji=Emoji.from_str("\N{Leftwards Arrow with Hook}"))
    async def volver_anterior_carpeta(self, _boton: Button, interaccion: Interaction) -> None:
        """
        Vuelve a la carpeta anterior, si es posible.
        """
        self.pagina = 0
        self.ruta = partir_ruta(self.ruta)[0]
        self.refrescar_menu()
        await self.refrescar_mensaje(interaccion)


    @button(style=ButtonStyle.grey,
            custom_id="pg_back",
            row=2,
            emoji=Emoji.from_str("\N{Leftwards Black Arrow}"))
    async def pagina_anterior(self, _boton: Button, interaccion: Interaction) -> None:
        """
        Va a la página anterior.
        """
        self.pagina -= 1
        self.refrescar_menu()
        await self.refrescar_mensaje(interaccion)


    @button(style=ButtonStyle.grey,
            custom_id="pg_next",
            row=2,
            emoji=Emoji.from_str("\N{Black Rightwards Arrow}"))
    async def pagina_siguiente(self, _boton: Button, interaccion: Interaction) -> None:
        """
        Va a la página siguiente.
        """
        self.pagina += 1
        self.refrescar_menu()
        await self.refrescar_mensaje(interaccion)
