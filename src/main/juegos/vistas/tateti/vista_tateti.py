"""
Módulo para una vista de una partida de Tres en Raya.
"""

from typing import TYPE_CHECKING, Any, Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from ..vista_juego_abc import VistaJuegoBase
from ..vista_reiniciar_abc import VistaReiniciarBase, cerrar_partida

if TYPE_CHECKING:
    from ....botshot import BotShot
    from ...modelos import JuegoBase


class ReiniciarTaTeTi(VistaReiniciarBase):
    """
    Vista para reiniciar el Tres en Raya.
    """

    async def reiniciar_extra(self, interaccion: Interaction) -> None:
        """
        Reinicia el Tres en Raya.
        """

        self.maestra.modelo.opciones.cambiar_orden_jugadores() # Necesariamente primero
        self.maestra.modelo.reiniciar()
        await interaccion.message.edit(content=self.maestra.modelo.mensaje,
                                       view=VistaTaTeTi(self.maestra.bot, self.maestra.modelo))


class BotonCasilla(Button):
    """
    Boton de casilla de un Tres en Raya.
    """

    def __init__(self,
                 vista_maestra: "VistaTaTeTi",
                 col: int,
                 fil: int) -> None:
        """
        Inicializa un botón de casilla.
        """

        super().__init__(label=" ",
                         custom_id=f"tictactoe_{col}_{fil}",
                         style=ButtonStyle.gray,
                         row=fil)

        self.maestra: "VistaTaTeTi" = vista_maestra
        self.col: int = col
        self.fil: int = fil


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Un jugador apretó la casilla.
        """

        await self.maestra.seguir(col=self.col,
                                  fil=self.fil,
                                  interaccion=interaccion,
                                  boton=self)


class VistaTaTeTi(VistaJuegoBase):
    """
    Vista de Tres en Raya.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase") -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(bot=bot,
                         modelo=modelo)

        for j in range(3):
            for i in range(3):
                self.add_item(BotonCasilla(vista_maestra=self,
                                           col=i,
                                           fil=j))


    def es_jugador_actual(self, id_jugador: str) -> bool:
        """
        Determina si es el jugador actual.
        """

        return id_jugador == self.modelo.jugador_actual.id


    async def actualizar_mensaje(self,
                                 interaccion: Interaction,
                                 mensaje: Optional[str]=None):
        """
        Actualiza el mensaje de la partida.
        """

        if not self.modelo.terminado():
            await interaccion.response.edit_message(content=mensaje,
                                                    view=self)
            return

        msg = ((f"Victoria para **{self.modelo.jugador_actual.nombre} " +
                f"({self.modelo.ficha_actual})**")
                if not self.modelo.empate()
                else "Es un empate.")

        self.clear_items()
        jug = self.modelo.cantidad_jugadores
        await interaccion.response.edit_message(content=msg + f"\n\n¿Otra partida? **(0 / {jug})**",
                                                view=ReiniciarTaTeTi(vista_maestra=self))


    async def seguir(self,
                     col: int,
                     fil: int,
                     interaccion: Interaction,
                     boton: Button,
                     mensaje: Optional[str]=None) -> None:
        """
        Prosigue con el juego.
        """

        autor = interaccion.user

        if not self.es_jugador_actual(str(autor.id)):
            msg = (self.modelo.mensaje + 
                   f"\n\nPero, {autor.mention}, o vos no estás jugando o a vos no te toca.")
            await self.actualizar_mensaje(interaccion, msg)
            return

        if self.modelo.actualizar(col=col, fil=fil):
            boton.emoji = Emoji.from_str(self.modelo.casilla(col, fil))
            boton.label = None # Para que no haya espacios vacíos raros
        await self.actualizar_mensaje(interaccion, mensaje or self.modelo.mensaje)


    @button(label="Cerrar",
            custom_id="tictactoe_close",
            style=ButtonStyle.gray,
            emoji=Emoji.from_str("\U0001F6D1"),
            row=4)
    async def cerrar_tateti(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Cierra la partida.
        """

        await cerrar_partida(interaccion)
