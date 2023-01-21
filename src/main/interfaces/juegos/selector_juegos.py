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
    from discord import Message

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
        lista_juegos=list(self.selector.juegos.values())[desde:hasta]

        opciones = [SelectOption(label=' '.join(juego.nombre_juego().split('_')),
                                 value=juego.nombre_juego(),
                                 description=juego.descripcion_juego(),
                                 emoji=(juego.elegir_emoji()))
                                 for juego in lista_juegos]

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
        clase_manejador =  self.selector.juegos[eleccion]
        await self.selector.iniciar_lobby(clase_manejador=clase_manejador,
                                          interaccion=interaccion,
                                          bot=self.selector.bot,
                                          editar=True)

        


class SelectorJuegos(Paginador):
    """
    Clase para seleccionar un juego que iniciar.
    """

    max_elementos_por_pagina: int = 5

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


    @staticmethod
    async def iniciar_lobby(*,
                            clase_manejador: "ManejadorBase",
                            interaccion: Interaction,
                            bot: "BotShot",
                            editar: bool=True) -> None:
        """
        Crea una instancia de manejador, de Lobby y envía ya
        el mensaje para interactuar.
        """

        autor = interaccion.user

        msg = f"Creando partida de `{clase_manejador.nombre_juego()}`!"
        # Este es para apaciguar el interaction.response
        if editar:
            # El mensaje a editar ya tiene que ser efímero
            await interaccion.response.edit_message(content=msg, view=None)
        else:
            # Si se einvía view no puede ser None
            await interaccion.response.send_message(content=msg, ephemeral=True)
        # Este es el de verdad
        mens: "Message" = await interaccion.channel.send(content="*Creando lobby...*")

        host = Jugador.desde_usuario_discord(autor)
        jugadores = [host]
        clase_manejador = clase_manejador(bot=bot,
                                          jugadores=jugadores,
                                          usuario_creador=autor,
                                          mensaje_raiz=mens,
                                          **interaccion.extras)
        lobby = Lobby(manejador=clase_manejador,
                      mensaje_raiz=mens)


        await mens.edit(content=msg,
                        embed=clase_manejador.refrescar_embed(),
                        view=lobby)
