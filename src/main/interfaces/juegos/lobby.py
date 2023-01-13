"""
Módulo para esperar a iniciar un juego.
"""

from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View, button

from ...juegos import Jugador

if TYPE_CHECKING:
    from ...juegos.manejadores import ManejadorBase


class Lobby(View):
    """
    Sala de espera para juegos.
    """

    def __init__(self,
                 manejador: "ManejadorBase",
                 timeout: Optional[float]=300.0) -> None:
        """
        Inicializa una instancia de 'SLobby'.
        """

        super().__init__(timeout=timeout)

        self.clase_juego: type["ManejadorBase"] = type(manejador)
        self.manejador: "ManejadorBase" = manejador
        self.jugador_host: Jugador = manejador.lista_jugadores[0] # Siempre será el primero


    def es_host(self, id_usuario: str) -> bool:
        """
        Determina si una persona es el host de la partida.
        """

        return id_usuario == self.jugador_host.id


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

        if str(autor.id) in list(jug.id for jug in self.manejador.lista_jugadores):
            mensaje = f"{autor.mention}, *vos ya estás unido.*"
        elif self.manejador.cantidad_jugadores >= self.manejador.max_jugadores:
            mensaje = "Cantidad máxima de jugadores alcanzada."
        else:
            self.manejador.lista_jugadores.append(Jugador(autor.display_name, str(autor.id)))

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

        if str(autor.id) == self.jugador_host.id:
            mensaje = f"{autor.mention}, vos sos el anfitrión, no podés salir sin cerrar el lobby."
        elif str(autor.id) not in list(jug.id for jug in self.manejador.lista_jugadores):
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
            msg = (f"{autor.mention}: sólo el host, **{self.jugador_host.nombre}**, puede " +
                    "iniciar la partida.")
            self.actualizar_botones()
            await self.refrescar_mensaje(interaccion, msg)
            return

        self.manejador.iniciar_modelo()
        await interaccion.response.edit_message(content=self.manejador.modelo.mensaje,
                                                embed=None,
                                                view=self.manejador.vista_modelo)


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
