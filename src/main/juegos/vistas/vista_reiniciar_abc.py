"""
Vista que pregunta por otra partida de un juego.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from discord import ButtonStyle, Interaction
from discord import PartialEmoji as Emoji
from discord.ui import Button, View, button

if TYPE_CHECKING:
    from ..jugador import ListaJugadores
    from .vista_juego_abc import VistaJuegoBase


async def cerrar_partida(interaccion: Interaction) -> None:
    """
    Función auxiliar para cerrar una partida.
    """

    await interaccion.message.delete()
    await interaccion.response.send_message(content="*Terminando partida...*",
                                            delete_after=5.0)


class VistaReiniciarBase(ABC, View):
    """
    Vista para reiniciar una partida.
    """

    def __init__(self, vista_maestra: "VistaJuegoBase"):
        """
        Inicializa la vista para reiniciar.
        """

        super().__init__(timeout=None)

        self.maestra: "VistaJuegoBase" = vista_maestra
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


    @abstractmethod
    async def reiniciar_extra(self, interaccion: Interaction) -> None:
        """
        Operaciones extra obligatorias a realizar si se reinicia la partida.
        """

        raise NotImplementedError


    @button(style=ButtonStyle.green,
            label="Sí",
            disabled=False,
            custom_id="restart_yes",
            emoji=Emoji.from_str("\U00002705"),
            row=0)
    async def reiniciar_si(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Se reinicia la partida.
        """

        autor = interaccion.user

        if not self.maestra.modelo.existe_jugador(id_jugador=str(autor.id)):
            msg = f"{autor.mention}, vos no sos un jugador de esta partida."
            await interaccion.response.edit_message(content=msg)
            return


        elif self._jugador_acepto(str(autor.id)):
            msg = f"{autor.mention}, vos ya aceptaste reiniciar la partida."
            await interaccion.response.edit_message(content=msg)
            return

        else:
            jug = self.maestra.modelo.get_jugador(str(autor.id))
            self.jugadores_aceptaron.append(jug)
            msg = (f"Reiniciando partida... **({self.aceptaciones} / " +
                   f"{self.maestra.modelo.cantidad_jugadores})**")
            await interaccion.response.edit_message(content=msg)

        if self.aceptaciones == self.maestra.modelo.cantidad_jugadores:
            await self.reiniciar_extra(interaccion)


    @button(style=ButtonStyle.red,
            label="No",
            disabled=False,
            custom_id="restart_no",
            emoji=Emoji.from_str("\U0000274E"),
            row=0)
    async def reiniciar_no(self, interaccion: Interaction, _boton: Button) -> None:
        """
        No se reinicia la partida.
        """

        await cerrar_partida(interaccion)
