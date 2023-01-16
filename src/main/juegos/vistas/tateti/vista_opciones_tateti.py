"""
Módulo para la vista e las opciones del Tres en Raya.
"""

from discord import Interaction, ButtonStyle
from discord.ui import button, Button

from ..vista_opciones_abc import VistaOpcionesBase


class VistaOpcionesTaTeTi(VistaOpcionesBase):
    """
    Vista de opciones de Tres en Raya.
    """

    @button(label="Empieza primer jugador",
            custom_id="prop_player_1_first",
            disabled=False,
            style=ButtonStyle.primary,
            row=0)
    async def cambiar_primer_jugador(self, interaccion: Interaction, boton: Button) -> None:
        """
        Cambia el jugador que va primero.
        """

        primero_el_1 = self.opciones.cambiar_orden_jugadores()

        if primero_el_1:
            boton.label = "Empieza primer jugador"
        else:
            boton.label = "Empieza segundo jugador"

        await self.refrescar_mensaje(interaccion=interaccion,
                                     mensaje=f"Cambiado opción a `{boton.label}`...")

