"""
Módulo para esperar a iniciar un juego.
"""

from typing import TYPE_CHECKING, Any, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View, button

from ...juegos import Jugador

if TYPE_CHECKING:
    from discord import Message

    from ...juegos.manejadores import ManejadorBase


class BotonOpciones(Button):
    """
    Botón para entrar en opciones.
    """

    def __init__(self, lobby: "Lobby"):
        """
        Inicializa una instancia de 'BotonOpciones'.        
        """

        super().__init__(style=ButtonStyle.gray,
                         label="Opciones",
                         disabled=False,
                         custom_id="game_options",
                         emoji=Emoji.from_str("\U00002699"),
                         row=3)

        self.lobby: "Lobby" = lobby


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El usuario seleccionó las opciones.
        Se da por hecho que las opciones y su vista no son `None`.
        """

        autor = interaccion.user

        if not self.lobby.jugador_unido(str(autor.id)):
            msg = f"{autor.mention}, capo, como que vos no estás unido y tal..."
            await interaccion.response.edit_message(content=msg,
                                                    view=self)
            return

        opciones = self.lobby.manejador.opciones
        vista_opciones = self.lobby.manejador.vista_opciones
        
        await interaccion.response.edit_message(content=opciones.mensaje,
                                                view=vista_opciones)


class Lobby(View):
    """
    Sala de espera para juegos.
    """

    def __init__(self,
                 manejador: "ManejadorBase",
                 mensaje_raiz: Optional["Message"]) -> None:
        """
        Inicializa una instancia de 'Lobby'.
        """

        super().__init__(timeout=900.0)

        self.clase_juego: type["ManejadorBase"] = type(manejador)
        self.manejador: "ManejadorBase" = manejador
        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        if self.manejador.hay_opciones():
            self.add_item(BotonOpciones(self))
            if self.manejador.vista_opciones.menu_anterior is None:
                self.manejador.vista_opciones.menu_anterior = self

        self.actualizar_botones()


    async def on_timeout(self) -> None:
        """
        Pasó el tiempo.
        """

        self.clear_items()
        if self.mensaje_raiz is not None:
            await self.mensaje_raiz.edit(content="*Tiempo agotado. Cerrando...*",
                                         delete_after=5.0)


    def es_host(self, id_usuario: str) -> bool:
        """
        Determina si una persona es el host de la partida.
        """

        return id_usuario == self.manejador.jugador_host.id


    def jugador_unido(self, id_usuario: str) -> bool:
        """
        Determina si un jugador está unido.
        """

        for jugador in self.manejador.lista_jugadores:
            if id_usuario == jugador.id:
                return True

        return False


    async def refrescar_mensaje(self,
                                interaccion: Interaction,
                                mensaje: Optional[str]=None) -> None:
        """
        Refresca el mensaje del lobby.
        """

        embed = self.manejador.refrescar_embed()

        await interaccion.response.edit_message(content=mensaje,
                                                embed=embed,
                                                view=self)


    def actualizar_boton(self, boton: Button) -> None:
        """
        Oculta el botón dependiendo de unas condiciones.
        """

        boton.disabled = any(((boton.custom_id == "game_start"
                               and not self.manejador.hay_suficientes()),
                            )
                        )


    def actualizar_botones(self) -> None:
        """
        Desactiva los botones o no dependiendo de
        ciertas condiciones.
        """
        for item in self.children:
            if isinstance(item, Button):
                self.actualizar_boton(item)


    @button(label="Unirse",
            style=ButtonStyle.green,
            custom_id="lobby_join",
            row=3)
    async def jugador_se_une(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Un jugador trata de unirse a la partida.
        """

        autor = interaccion.user
        mensaje = None

        if self.jugador_unido(str(autor.id)):
            mensaje = f"{autor.mention}, *vos ya estás unido.*"
        elif self.manejador.cantidad_jugadores >= self.manejador.max_jugadores:
            mensaje = "Cantidad máxima de jugadores alcanzada."
        else:
            self.manejador.lista_jugadores.append(Jugador.desde_usuario_discord(autor))

        self.actualizar_botones()
        await self.refrescar_mensaje(interaccion, mensaje)


    @button(label="Salirse",
            style=ButtonStyle.red,
            custom_id="lobby_exit",
            row=3)
    async def jugador_se_sale(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Un jugador trata de unirse a la partida.
        """

        autor = interaccion.user
        mensaje = None

        if self.es_host(str(autor.id)):
            mensaje = f"{autor.mention}, vos sos el anfitrión, no podés salir sin cerrar el lobby."
        elif not self.jugador_unido(str(autor.id)):
            mensaje = f"{autor.mention}, *vos no estás unido.*"
        else:
            for jugador in self.manejador.lista_jugadores:
                if jugador.id == str(autor.id):
                    self.manejador.lista_jugadores.remove(jugador)
                    break

        self.actualizar_botones()
        await self.refrescar_mensaje(interaccion, mensaje)


    @button(label="Iniciar",
            style=ButtonStyle.secondary,
            custom_id="game_start",
            disabled=True,
            row=3,
            emoji=Emoji.from_str("\U0001F579"))
    async def iniciar_juego(self, interaccion: Interaction, _boton: Button) -> None:
        """
        El juego inicia.
        """

        autor = interaccion.user

        if self.manejador.cantidad_jugadores < self.manejador.min_jugadores:
            restantes = self.manejador.min_jugadores - self.manejador.cantidad_jugadores
            msg = (f"**Cantidad de jugadores insuficiente.** Falta{'n' if restantes > 1 else ''} " +
                   f"`{restantes}` jugador{'es' if restantes > 1 else ''}.")
            self.actualizar_botones()
            await self.refrescar_mensaje(interaccion, msg)
            return

        if not self.es_host(str(autor.id)):
            host = self.manejador.jugador_host
            msg = (f"{autor.mention}: sólo el host, **{host.nombre}**, puede " +
                    "iniciar la partida.")
            self.actualizar_botones()
            await self.refrescar_mensaje(interaccion, msg)
            return

        self.manejador.iniciar_modelo()
        await interaccion.response.edit_message(content=self.manejador.modelo.mensaje,
                                                embed=None,
                                                view=self.manejador.vista_modelo)
        await self.manejador.vista_modelo.setup()


    @button(style=ButtonStyle.gray,
            custom_id="lobby_close",
            row=4,
            emoji=Emoji.from_str("\U0000274C"))
    async def cierra_lobby(self, interaccion: Interaction, _boton: Button) -> None:
        """
        El host cerró el lobby por completo.
        """

        autor = interaccion.user

        if not self.es_host(str(autor.id)):
            self.actualizar_botones()
            await self.refrescar_mensaje(interaccion, (f"{autor.mention}, vos no sos el " +
                                                        "anfitrión. No podés cerrar el lobby."))
            return

        await interaccion.message.delete()
        await interaccion.response.send_message(content="*Cerrando lobby...*",
                                                delete_after=5.0)
