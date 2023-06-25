"""
Vista que pregunta por otra partida de un juego.
"""

from typing import TYPE_CHECKING, Any, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button, View, button

from .auxiliar import BotonContador, cerrar_partida

if TYPE_CHECKING:
    from .vista_juego_abc import VistaJuegoBase
    from ..jugador import Jugador


class BotonConfirmarReinicio(BotonContador):
    """
    Botón para confirmar que se quiere reiniciar
    la partida.
    """

    async def accion(self) -> Any:
        """
        Realiza la acción del botón contador.
        """

        await self.maestra.reiniciar_vista()


class VistaReiniciarBase(View):
    """
    Vista para reiniciar una partida.
    """

    def __init__(self, vista_maestra: "VistaJuegoBase"):
        """
        Inicializa la vista para reiniciar.
        """

        super().__init__(timeout=None)

        self.maestra: "VistaJuegoBase" = vista_maestra
        self.boton_contador: BotonConfirmarReinicio = BotonConfirmarReinicio(
            maestra=self,
            mensaje="Sí",
            estilo=ButtonStyle.green,
            emoji="\U00002705",
            row=0
        )
        self.add_item(self.boton_contador)


    @property
    def cantidad_jugadores(self) -> int:
        """
        Devuelve la cantidad de jugadores.
        """

        return self.maestra.cantidad_jugadores


    def get_jugador(self, id_jugador: str) -> Optional["Jugador"]:
        """
        Devuelve un jugador unido según el ID, si lo encuentra.

        Sino devuelve `None`.
        """

        return self.maestra.get_jugador(id_jugador=id_jugador)


    def existe_jugador(self, *, id_jugador: str) -> bool:
        """
        Basado en el id de un jugador, decide si el pasado está
        entre los jugadores actuales.
        """

        return self.maestra.existe_jugador(id_jugador=id_jugador)


    async def reiniciar_extra(self) -> None:
        """
        Operaciones extra a realizar antes de reiniciar la partida.
        """

        return


    async def reiniciar_vista(self) -> None:
        """
        Reinicia definitivamente la vista maestra.
        """

        await self.reiniciar_extra()

        self.maestra.modelo.reiniciar()
        self.maestra = self.maestra.clonar()
        await self.maestra.mensaje_raiz.edit(content=self.maestra.modelo.mensaje,
                                             view=self.maestra)

        await self.maestra.setup()


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
