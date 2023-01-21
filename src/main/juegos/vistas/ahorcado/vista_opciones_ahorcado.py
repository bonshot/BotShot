"""
Módulo para la vista de las opciones del Ahorcado.
"""

from typing import Optional
from re import sub

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle, TextStyle
from discord.ui import Button, Modal, TextInput, button

from ..vista_opciones_abc import VistaOpcionesBase

MENOS: str = "\U00002796"
MAS: str = "\U00002795"


class CambiaVidas(Modal):
    """
    Modal para cambiar las vidas a usar del Ahorcado.
    """

    vidas: TextInput = TextInput(label="Vidas",
                                 style=TextStyle.short,
                                 custom_id="hanged_lives_select",
                                 placeholder="Escribe un número mayor o igual a 1",
                                 required=True,
                                 row=0)


    def __init__(self,
                 vista_maestra: "VistaOpcionesAhorcado",
                 boton: Button) -> None:
        """
        Inicializa el modal de las vidas del Ahorcado.
        """

        super().__init__(timeout=None,
                         title="Elige cuántas vidas usar",
                         custom_id="hanged_lives_select_modal")

        self.maestra: "VistaOpcionesAhorcado" = vista_maestra
        self.boton: Button = boton


    def _es_int_valido(self, num: str) -> bool:
        """
        Decide si un string representa un número entero y es
        apto para usar como valor de vidas.
        """

        try:
            int(num)
        except:
            return False
        else:
            return int(num) >= 1


    async def on_submit(self, interaccion: Interaction) -> None:
        """
        Procesa la cantidad de vidas elegida.
        """

        if not self._es_int_valido(self.vidas.value):
            msg = (f"{interaccion.user.mention}, `{self.vidas.value}` no es un " +
                   "número de vidas válido.")
            await self.maestra.refrescar_opciones(interaccion,
                                                  self.boton,
                                                  msg)
            return

        await self.maestra.procesar_vidas(interaccion, self.boton, int(self.vidas.value))


class CambiaFrases(Modal):
    """
    Modal para cambiar la frase del Ahorcado.
    """

    frase: TextInput = TextInput(label="Frase",
                                 style=TextStyle.short,
                                 custom_id="hanged_phrase_select",
                                 placeholder="Escribe una frase breve",
                                 required=True,
                                 row=0)


    def __init__(self,
                 vista_maestra: "VistaOpcionesAhorcado",
                 boton: Button) -> None:
        """
        Inicializa el modal de la frase del Ahorcado.
        """

        super().__init__(timeout=None,
                         title="Elige la frase a usar",
                         custom_id="hanged_phrase_select_modal")

        self.maestra: "VistaOpcionesAhorcado" = vista_maestra
        self.boton: Button = boton


    async def on_submit(self, interaccion: Interaction) -> None:
        """
        Procesa la frase elegida.
        """

        fr = self.frase.value.strip()
        msg = (f"Cambiando la frase a `{self.maestra.ofus(fr)}`..."
               if bool(fr)
               else "Dejando la frase como está...")

        await self.maestra.procesar_frase(interaccion, self.boton, fr, msg)


class VistaOpcionesAhorcado(VistaOpcionesBase):
    """
    Vista de opciones del Ahorcado.
    """

    vidas_label: str = "Vidas:"
    frase_label: str = "Frase:"

    vidas_id: str = "hanged_lives"
    frase_id: str = "hanged_phrase"


    def ofus(self, frase: str) -> str:
        """
        Oculta la frase.
        """

        return sub(r"\w", "*", frase).strip()


    async def procesar_vidas(self,
                             interaccion: Interaction,
                             boton: Button,
                             vidas: int,
                             msg: Optional[str]=None) -> None:
        """
        Procesa la cantidad de vidas elegida en el modal.
        """

        vid = self.opciones.cambiar_vidas(vidas)

        if msg is None:
            msg = f"Cambiando número de vidas a `{vid}`..."

        await self.refrescar_opciones(interaccion, boton, msg)


    async def procesar_frase(self,
                             interaccion: Interaction,
                             boton: Button,
                             frase: str,
                             msg: Optional[str]=None) -> None:
        """
        Procesa la frase elegida en el modal.
        """

        self.opciones.cambiar_frase(frase)

        await self.refrescar_opciones(interaccion, boton, msg)


    def actualizar_boton_extra(self, boton: Button) -> None:
        """
        Actualiza cada boton por separado.
        """

        boton.disabled = any(((boton.custom_id == f"{self.vidas_id}_minus"
                               and self.opciones.vidas <= 1),
                            )
                        )

        if boton.custom_id == self.frase_id:
            ofus_fr = self.ofus(self.opciones.frase)

            if bool(self.opciones.frase.strip()):
                fra = ofus_fr
                estilo = ButtonStyle.gray
            else:
                fra = "Aleatoria"
                estilo = ButtonStyle.primary

            boton.label = f"{self.frase_label} {fra}"
            boton.style = estilo

        elif boton.custom_id == self.vidas_id:
            boton.label = f"{self.vidas_label} {self.opciones.vidas}"


    @button(custom_id=f"{vidas_id}_minus",
            disabled=False,
            style=ButtonStyle.gray,
            emoji=Emoji.from_str(MENOS),
            row=0)
    async def ahorcado_menos_vidas(self, interaccion: Interaction, boton: Button) -> None:
        """
        Resta el número de vidas.
        """

        if self.opciones.vidas > 1:
            vid = self.opciones.vidas - 1
            await self.procesar_vidas(interaccion,
                                      boton,
                                      vid,
                                      f"Disminuyendo el número de vidas a `{vid}`...")
        else:
            await self.refrescar_opciones(interaccion,
                                          boton,
                                          "No se puede bajar más el número de vidas.")


    @button(label=f"{vidas_label} 7",
            custom_id=vidas_id,
            disabled=False,
            style=ButtonStyle.gray,
            row=0)
    async def ahorcado_vidas(self, interaccion: Interaction, boton: Button) -> None:
        """
        Cambia el número de vidas.
        """

        await interaccion.response.send_modal(CambiaVidas(self, boton))


    @button(custom_id=f"{vidas_id}_mas",
            disabled=False,
            style=ButtonStyle.gray,
            emoji=Emoji.from_str(MAS),
            row=0)
    async def ahorcado_mas_vidas(self, interaccion: Interaction, boton: Button) -> None:
        """
        Suma el número de vidas.
        """

        vid = self.opciones.vidas + 1
        await self.procesar_vidas(interaccion,
                                  boton,
                                  vid,
                                  f"Aumentando el número de vidas a `{vid}`...")


    @button(label=f"{frase_label} Aleatoria",
            custom_id=frase_id,
            disabled=False,
            style=ButtonStyle.primary,
            row=1)
    async def ahorcado_frase(self, interaccion: Interaction, boton: Button) -> None:
        """
        Cambia la frase a utilizar.
        """

        await interaccion.response.send_modal(CambiaFrases(self, boton))
