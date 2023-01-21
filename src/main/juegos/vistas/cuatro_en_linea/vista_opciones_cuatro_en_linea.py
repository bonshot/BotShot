"""
Módulo para la vista de las opciones del 4 en Línea.
"""

from discord import Interaction, ButtonStyle
from discord.ui import button, Button

from ..vista_opciones_abc import VistaOpcionesBase


class VistaOpcionesCuatroEnLinea(VistaOpcionesBase):
    """
    Vista de opciones del 4 en Línea.
    """

    jugador_label: str = "Primero va el jugador"
    modo_texto_label: str = "Modo Texto:"
    colores_default_label: str = "Colores Predeterminados:"


    @button(label=f"{modo_texto_label} OFF",
            custom_id="connect_four_prop_text_mode",
            disabled=False,
            style=ButtonStyle.red,
            row=0)
    async def activar_modo_texto(self, interaccion: Interaction, boton: Button) -> None:
        """
        Activa o desactiva el modo de texto.
        """

        activado = self.opciones.cambiar_modo_texto()
        self.refrescar_boton_binario(boton, self.modo_texto_label, activado)

        await self.refrescar_opciones(interaccion, boton)


    @button(label=f"{jugador_label} 1",
            custom_id="connect_four_prop_player_1_first",
            disabled=False,
            style=ButtonStyle.primary,
            row=1)
    async def cambiar_primer_jugador(self, interaccion: Interaction, boton: Button) -> None:
        """
        Cambia el jugador que va primero.
        """

        primero_el_1 = self.opciones.cambiar_orden_jugadores()

        if primero_el_1:
            boton.label = f"{self.jugador_label} 1"
        else:
            boton.label = f"{self.jugador_label} 2"

        await self.refrescar_opciones(interaccion, boton)


    @button(label=f"{colores_default_label} OFF",
            custom_id="connect_four_prop_default_colors",
            disabled=False,
            style=ButtonStyle.red,
            row=0)
    async def cambiar_a_colores_predeterminados(self,
                                                interaccion: Interaction,
                                                boton: Button) -> None:
        """
        Decide si usar los colores predeterminados.
        """

        activado = self.opciones.usar_colores_default()
        self.refrescar_boton_binario(boton, self.colores_default_label, activado)

        await self.refrescar_opciones(interaccion, boton)
