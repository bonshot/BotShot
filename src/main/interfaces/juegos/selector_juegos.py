"""
Módulo para seleccionar un juego.
"""

from typing import TYPE_CHECKING, Optional, TypeAlias

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord import SelectOption
from discord.enums import ButtonStyle
from discord.ui import Button, Select, View, button

from ...juegos import Jugador
from ...juegos.manejadores import ManejadorBase
from .lobby import Lobby

if TYPE_CHECKING:
    from ...juegos.manejadores import ListaManejadores


DicManejadores: TypeAlias = dict[str, type[ManejadorBase]]


class MenuJuegos(Select):
    """
    Clase para el menú con el que seleccionar juegos.
    """

    def __init__(
        self,
        *,
        juegos: DicManejadores,
        lista_nombres_juegos: list[str],
        custom_id: str="menu_selector_juegos",
        placeholder: Optional[str]="Seleccione un juego",
        min_values: int=1,
        max_values: int=1,
        disabled: bool=False,
        row: Optional[int]=1
    ) -> None:
        """
        Inicializa una instancia de 'MenuJuegos'.
        """

        self.juegos: DicManejadores = juegos
        opciones = [SelectOption(label=' '.join(nombre_juego.split('_')), value=nombre_juego)
                                 for nombre_juego in lista_nombres_juegos]

        super().__init__(custom_id=custom_id,
                         placeholder=placeholder,
                         min_values=min_values,
                         max_values=max_values,
                         options=opciones,
                         disabled=disabled,
                         row=row)


    async def callback(self, interaccion: Interaction) -> None:
        """
        Procesa la opción elegida.
        """

        eleccion = self.values[0]
        autor = interaccion.user

        jugadores = [Jugador(nombre=autor.display_name,
                             id=str(autor.id))]
        manejador = self.juegos[eleccion](jugadores=jugadores,
                                         **interaccion.extras)

        await interaccion.response.edit_message(content=f"Creando partida de `{eleccion}`!",
                                                embed=manejador.refrescar_embed(),
                                                view=Lobby(manejador=manejador))


class SelectorJuegos(View):
    """
    Clase para seleccionar un juego que iniciar.
    """

    def __init__(self,
                 manejadores: "ListaManejadores"=ManejadorBase.lista_clases_manejadores,
                 pagina: int=0,
                 timeout: Optional[float]=300.0) -> None:
        """
        Inicializa una instancia de 'SelectorJuegos'.
        """
        super().__init__(timeout=timeout)
        self.pagina: int = pagina
        self.menu_juegos: Optional[MenuJuegos] = None
        self.juegos: DicManejadores = {}

        for manejador in manejadores:
            self.juegos[manejador.nombre_juego()] = manejador

        self.refrescar_menu_juegos()


    @property
    def cantidad_elementos(self) -> int:
        """
        Devuelve la cantidad de elementos disponible en la pagina.
        """

        max_elementos = 20

        return (max_elementos
                if self.cantidad_juegos > max_elementos
                else self.cantidad_juegos)


    @property
    def cantidad_juegos(self) -> int:
        """
        Devuelve la cantidad de juegos disponibles.
        """
        return len(self.juegos)


    @property
    def max_paginas(self) -> int:
        """
        Devuelve el límite de páginas a obedecer.
        Esto se usa para bloquear botones de ser necesario.
        """

        if not self.cantidad_elementos:
            return 0

        return ((self.cantidad_juegos // self.cantidad_elementos) +
                (1 if self.cantidad_juegos % self.cantidad_elementos else 0))


    def generar_menu_juegos(self) -> MenuJuegos:
        """
        Genera un nuevo menú de juegos.
        """
        desde = self.pagina * self.cantidad_elementos
        hasta = (self.pagina + 1) * self.cantidad_elementos

        return MenuJuegos(juegos=self.juegos,
                          lista_nombres_juegos=list(self.juegos.keys())[desde:hasta])


    def refrescar_menu_juegos(self) -> None:
        """
        Agrega el menú a la vista, y elimina el anterior, si había uno.
        """
        self.remove_item(self.menu_juegos)
        self.menu_juegos = self.generar_menu_juegos()
        self.add_item(self.menu_juegos)
        self.actualizar_botones()


    async def refrescar_mensaje(self, interaccion: Interaction) -> None:
        """
        Refresca el mensaje con una nueva vista.
        """

        await interaccion.response.edit_message(view=self)


    def actualizar_boton(self, boton: Button) -> None:
        """
        Oculta el botón dependiendo de la página actual.
        """

        boton.disabled = any(((boton.custom_id == "pg_back" and self.pagina <= 0),
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


    @button(style=ButtonStyle.grey,
            custom_id="pg_back",
            row=2,
            emoji=Emoji.from_str("\U00002B05"))
    async def pagina_anterior(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Va a la página anterior.
        """
        self.pagina -= 1
        self.refrescar_menu_juegos()
        await self.refrescar_mensaje(interaccion)


    @button(style=ButtonStyle.grey,
            custom_id="pg_next",
            row=2,
            emoji=Emoji.from_str("\U000027A1"))
    async def pagina_siguiente(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Va a la página siguiente.
        """
        self.pagina += 1
        self.refrescar_menu_juegos()
        await self.refrescar_mensaje(interaccion)
