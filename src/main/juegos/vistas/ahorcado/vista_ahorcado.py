"""
Módulo para la vista de una partida de Ahorcado.
"""

from typing import Optional

from discord import Interaction
from discord.enums import ButtonStyle, TextStyle
from discord.ui import Button, Modal, TextInput, button

from ..vista_juego_abc import VistaJuegoBase
from ..vista_reiniciar_abc import VistaReiniciarBase


class VistaReiniciarAhorcado(VistaReiniciarBase):
    """
    Vista para reiniciar el Ahorcado.
    """


class AdivinarLetra(Modal):
    """
    Modal para adivinar una letra del ahorcado.
    """

    letra: TextInput = TextInput(label="Letra",
                                 style=TextStyle.short,
                                 custom_id="hanged_guess_select",
                                 placeholder="Escribe una única letra",
                                 required=True,
                                 min_length=1,
                                 max_length=1,
                                 row=0)

    def __init__(self, vista_maestra: "VistaAhorcado") -> None:
        """
        Inicializa el modal para adivinar letras.
        """

        super().__init__(timeout=None,
                         title="Elige la letra a usar",
                         custom_id="hanged_guess_select_modal")

        self.maestra: "VistaAhorcado" = vista_maestra


    async def on_submit(self, interaccion: Interaction) -> None:
        """
        Procesa la letra elegida.
        """

        await self.maestra.procesar_letra(interaccion, self.letra.value)


class VistaAhorcado(VistaJuegoBase):
    """
    Vista de una partida de Ahorcado.
    """

    @staticmethod
    def get_cerrar_id() -> str:
        """
        El ID del botón para cerrar la vista.
        """

        return "hanged_close"


    async def procesar_letra(self, interaccion: Interaction, letra: str) -> None:
        """
        Procesa la letra elegida.
        """

        autor = interaccion.user

        if self.get_jugador(str(autor.id)) is None:
            msg = (f"Pero, {autor.mention}, vos no estás jugando.\n\n" + 
                   self.modelo.mensaje)
            await self.refrescar_mensaje(interaccion, msg)
            return

        self.modelo.actualizar(letra=letra)
        await self.refrescar_mensaje(interaccion)


    async def refrescar_mensaje(self,
                                 interaccion: Interaction,
                                 mensaje: Optional[str]=None):
        """
        Actualiza el mensaje de la partida de Ahorcado.
        """

        if not self.modelo.terminado():
            msg = (self.modelo.mensaje if mensaje is None else mensaje)
            vista = self

        else:
            jug = self.get_jugador(str(interaccion.user.id))
            if self.modelo.victoria():
                extra = (f"¡Gloria para **{jug.nombre}**! " if jug is not None else "")
                msg = f"{extra}En efecto, la frase era `{self.modelo.get_frase()}`."
            else:
                extra = ((f"Verguenza para **{jug.nombre}**! Ha fastidiado la partida " +
                          f"cuando l")
                         if jug is not None else "L")
                msg = f"{extra}a frase era `{self.modelo.get_frase()}`."

            msg += f"\n\n ¿Otra partida? **(0 / {self.modelo.cantidad_jugadores})**"
            vista = VistaReiniciarAhorcado(self)

        await interaccion.response.edit_message(content=msg,
                                                view=vista)


    @button(label="Adivinar",
            custom_id="hanged_guess",
            disabled=False,
            style=ButtonStyle.primary,
            row=0)
    async def ahorcado_adivinar(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Un jugador trata de adivinar una letra.
        """

        await interaccion.response.send_modal(AdivinarLetra(self))
