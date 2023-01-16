"""
Módulo para seleccionar un juego.
"""

from typing import TYPE_CHECKING, Optional, TypeAlias

from discord import Interaction, SelectOption
from discord.ui import Select

from ...juegos import Jugador
from ...juegos.manejadores import ManejadorBase
from ...juegos.vistas import Paginador
from .lobby import Lobby

if TYPE_CHECKING:
    from ...botshot import BotShot
    from ...juegos.manejadores import ListaManejadores


DicManejadores: TypeAlias = dict[str, type[ManejadorBase]]


class MenuJuegos(Select):
    """
    Clase para el menú con el que seleccionar juegos.
    """

    def __init__(self,
                 *,
                 selector: "SelectorJuegos") -> None:
        """
        Inicializa una instancia de 'MenuJuegos'.
        """

        self.selector: "SelectorJuegos" = selector

        desde = self.selector.pagina * self.selector.cantidad_elementos
        hasta = (self.selector.pagina + 1) * self.selector.cantidad_elementos
        lista_nombres_juegos=list(self.selector.juegos.keys())[desde:hasta]

        opciones = [SelectOption(label=' '.join(nombre_juego.split('_')), value=nombre_juego)
                                 for nombre_juego in lista_nombres_juegos]

        super().__init__(custom_id="game_selection_menu",
                         placeholder="Seleccione un juego",
                         min_values=1,
                         max_values=1,
                         options=opciones,
                         disabled=False,
                         row=0)


    async def callback(self, interaccion: Interaction) -> None:
        """
        Procesa la opción elegida.
        """

        eleccion = self.values[0]
        autor = interaccion.user

        jugadores = [Jugador(nombre=autor.display_name,
                             id=str(autor.id))]
        manejador = self.selector.juegos[eleccion](bot=self.selector.bot,
                                                   jugadores=jugadores,
                                                   **interaccion.extras)

        await interaccion.response.edit_message(content=f"Creando partida de `{eleccion}`!",
                                                embed=manejador.refrescar_embed(),
                                                view=Lobby(manejador=manejador))


class SelectorJuegos(Paginador):
    """
    Clase para seleccionar un juego que iniciar.
    """

    def __init__(self,
                 bot: "BotShot",
                 manejadores: "ListaManejadores"=ManejadorBase.lista_clases_manejadores) -> None:
        """
        Inicializa una instancia de 'SelectorJuegos'.
        """

        self.menu_juegos: Optional[MenuJuegos] = None
        self.bot: "BotShot" = bot
        self.juegos: DicManejadores = {}

        for manejador in manejadores:
            self.juegos[manejador.nombre_juego()] = manejador

        super().__init__(manejadores)


    def refrescar_extra(self) -> None:
        """
        Operaciones extra a realizar al refrescar.
        """

        self.remove_item(self.menu_juegos)
        self.menu_juegos = MenuJuegos(selector=self)
        self.add_item(self.menu_juegos)
