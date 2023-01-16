"""
Módulo para una vista de una partida de Tres en Raya.
"""

from typing import Any, Optional, TYPE_CHECKING

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, button

from ..vista_juego_abc import VistaJuegoBase

if TYPE_CHECKING:
    from ...modelos import TaTeTi
    from ...jugador import ListaJugadores


async def _cerrar_partida(interaccion: Interaction) -> None:
    """
    Función auxiliar para cerrar una partida.
    """

    await interaccion.message.delete()
    await interaccion.response.send_message(content="*Terminando partida...*",
                                            delete_after=5.0)


class SiReiniciar(Button):
    """
    Botón para reiniciar el Tres en Raya.
    """

    def __init__(self, vista: "VistaTaTeTi"):
        """
        Inicializa una instancia de 'SiReiniciar'.        
        """

        super().__init__(style=ButtonStyle.green,
                         label="Sí",
                         disabled=False,
                         custom_id="restart_yes",
                         emoji=Emoji.from_str("\U00002705"),
                         row=0)

        self.vista: "VistaTaTeTi" = vista
        self.jugadores_aceptaron: "ListaJugadores" = []


    def _jugador_acepto(self, id_jugador: str) -> bool:
        """
        Determina por id si un jugador aceptó reiniciar la partida.
        """

        return any(id_jugador == jugador.id for jugador in self.jugadores_aceptaron)


    @property
    def aceptaciones(self) -> int:
        """
        Devuelve cuántos jugadores aceptaron reiniciar la partida.
        """

        return len(self.jugadores_aceptaron)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Se reinicia la partida.
        """

        autor = interaccion.user

        if not self.vista.modelo.existe_jugador(id_jugador=str(autor.id)):
            msg = f"{autor.mention}, vos no sos un jugador de esta partida."
            await interaccion.response.edit_message(content=msg)
            return


        elif self._jugador_acepto(str(autor.id)):
            msg = f"{autor.mention}, vos ya aceptaste reiniciar la partida."
            await interaccion.response.edit_message(content=msg)
            return

        else:
            jug = self.vista.modelo.get_jugador(str(autor.id))
            self.jugadores_aceptaron.append(jug)
            msg = (f"Reiniciando partida... **({self.aceptaciones} / " +
                   f"{self.vista.modelo.cantidad_jugadores})**")
            await interaccion.response.edit_message(content=msg)

        if self.aceptaciones == self.vista.modelo.cantidad_jugadores:
            self.vista.modelo.opciones.cambiar_orden_jugadores() # Necesariamente primero
            self.vista.modelo.reiniciar()
            await interaccion.message.edit(content=self.vista.modelo.mensaje,
                                           view=VistaTaTeTi(self.vista.bot, self.vista.modelo))


class NoReiniciar(Button):
    """
    Botón para cerrar el Tres en Raya.
    """

    def __init__(self, vista: "VistaTaTeTi"):
        """
        Inicializa una instancia de 'NoReiniciar'.        
        """

        super().__init__(style=ButtonStyle.red,
                         label="No",
                         disabled=False,
                         custom_id="restart_no",
                         emoji=Emoji.from_str("\U0000274E"),
                         row=0)

        self.vista: "VistaTaTeTi" = vista


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Se reinicia la partida.
        """

        await _cerrar_partida(interaccion)


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

        if not self.modelo.terminado():
            await interaccion.response.edit_message(content=mensaje,
                                                    view=self)
            return

        msg = ((f"Victoria para **{self.modelo.jugador_actual.nombre} " +
                f"({self.modelo.ficha_actual})**")
                if not self.modelo.empate()
                else "Es un empate.")

        self.clear_items()
        self.add_item(SiReiniciar(self))
        self.add_item(NoReiniciar(self))
        jug = self.modelo.cantidad_jugadores
        await interaccion.response.edit_message(content=msg + f"\n\n¿Otra partida? **(0 / {jug})**",
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


    @button(label="Cerrar",
            custom_id="tictactoe_close",
            style=ButtonStyle.gray,
            emoji=Emoji.from_str("\U0001F6D1"),
            row=4)
    async def cerrar_tateti(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Cierra la partida.
        """

        await _cerrar_partida(interaccion)
