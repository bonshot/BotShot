"""
Módulo para una vista de una partida de Tres en Raya.
"""

from typing import Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from ..vista_juego_abc import VistaJuegoBase


class VistaTaTeTi(VistaJuegoBase):
    """
    Vista de Tres en Raya.
    """

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

        if self.modelo.terminado():
            msg = ((f"Victoria para **{self.modelo.jugador_actual.nombre} " +
                   f"({self.modelo.ficha_actual})**")
                   if not self.modelo.empate()
                   else "Es un empate.")
            await interaccion.response.edit_message(content=msg,
                                                    view=None)
            await interaccion.message.delete(delay=5.0)
            return

        await interaccion.response.edit_message(content=mensaje,
                                                view=self)


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
        await self.actualizar_mensaje(interaccion, mensaje or self.modelo.mensaje)


    @button(label=" ",
            custom_id="tictactoe_0_0",
            style=ButtonStyle.gray,
            row=0)
    async def casilla_0_0(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (0, 0)
        """

        await self.seguir(col=0,
                          fil=0,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_1_0",
            style=ButtonStyle.gray,
            row=0)
    async def casilla_1_0(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (1, 0)
        """

        await self.seguir(col=1,
                          fil=0,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_2_0",
            style=ButtonStyle.gray,
            row=0)
    async def casilla_2_0(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (2, 0)
        """

        await self.seguir(col=2,
                          fil=0,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_0_1",
            style=ButtonStyle.gray,
            row=1)
    async def casilla_0_1(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (0, 1)
        """

        await self.seguir(col=0,
                          fil=1,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_1_1",
            style=ButtonStyle.gray,
            row=1)
    async def casilla_1_1(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (1, 1)
        """

        await self.seguir(col=1,
                          fil=1,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_2_1",
            style=ButtonStyle.gray,
            row=1)
    async def casilla_2_1(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (2, 1)
        """

        await self.seguir(col=2,
                          fil=1,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_0_2",
            style=ButtonStyle.gray,
            row=2)
    async def casilla_0_2(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (0, 2)
        """

        await self.seguir(col=0,
                          fil=2,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_1_2",
            style=ButtonStyle.gray,
            row=2)
    async def casilla_1_2(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (1, 2)
        """

        await self.seguir(col=1,
                          fil=2,
                          interaccion=interaccion,
                          boton=boton)


    @button(label=" ",
            custom_id="tictactoe_2_2",
            style=ButtonStyle.gray,
            row=2)
    async def casilla_2_2(self, interaccion: Interaction, boton: Button) -> None:
        """
        Un jugador apretó la casilla (2, 2)
        """

        await self.seguir(col=2,
                          fil=2,
                          interaccion=interaccion,
                          boton=boton)
