"""
Módulo para la vista de una partida de Piedra, Papel o Tijeras.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional, Self, TypeAlias

from discord import ButtonStyle, Interaction, Message
from discord import PartialEmoji as Emoji
from discord import User
from discord.ui import Button, View, button

from ...modelos import EMOJI_PAPEL, EMOJI_PIEDRA, EMOJI_TIJERAS, EleccionPPT
from ..vista_juego_abc import VistaJuegoBase
from ..vista_reiniciar_abc import VistaReiniciarBase

if TYPE_CHECKING:

    from ....botshot import BotShot
    from ...modelos import JuegoBase


DecidirFunc: TypeAlias = Callable[[Self, EleccionPPT], None]

CHECKMARK: str = "\U00002705"


class BotonComenzar(Button):
    """
    Botón para comenzar la partida.
    """

    def __init__(self, vista: "VistaPPT"):
        """
        Inicializa una instancia de 'BotonComenzar'.        
        """

        super().__init__(style=ButtonStyle.primary,
                         label="Comenzar",
                         disabled=False,
                         custom_id="ppt_start",
                         row=0)

        self.vista: "VistaPPT" = vista


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Comienza la partida.
        """

        await self.vista.comenzar(interaccion)


class ReiniciarPPT(VistaReiniciarBase):
    """
    Vista para reiniciar un juego de Piedra, Papel o Tijeras.
    """

    async def reiniciar_extra(self, interaccion: Interaction) -> None:
        """
        Reinicia el Piedra, Papel o Tijeras.
        """

        self.maestra.modelo.reiniciar()
        await interaccion.message.edit(content=self.maestra.modelo.mensaje,
                                       view=VistaPPT(self.maestra.bot, self.maestra.modelo))


class VistaPPT(VistaJuegoBase):
    """
    Vista de un Piedra, Papel o Tijeras.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase") -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(bot=bot, modelo=modelo)

        self.jugador_1, self.jugador_2 = self.modelo.jugadores
        self.nombre_eleccion_1: Optional[str] = None
        self.nombre_eleccion_2: Optional[str] = None
        self.add_item(BotonComenzar(self))


    async def comenzar(self, interaccion: Interaction) -> None:
        """
        Da comienzo al juego.
        Es necesario que esta función sea asincrónica.
        """

        self.clear_items()

        self.usuario_1: User = await self.bot.fetch_user(int(self.jugador_1.id))
        self.usuario_2: User = await self.bot.fetch_user(int(self.jugador_2.id))
        self.mensaje_original: Message = interaccion.message

        # Hay que crear referencias a los mensajes directos para después seguirlos
        msg = "**¡Elige! ¿Piedra, Papel o Tijeras?**"
        self.mensaje_1: Message = await self.usuario_1.send(content=msg,
                                                      view=VistaPPTPrivada(maestra=self,
                                                                           es_primer_jugador=True))
        self.mensaje_2: Message = await self.usuario_2.send(content=msg,
                                                      view=VistaPPTPrivada(maestra=self,
                                                                           es_primer_jugador=False))

        await interaccion.response.edit_message(content=self.modelo.mensaje,
                                                view=self)


    async def refrescar_mensaje(self,
                                mensaje: str,
                                vista: Optional[VistaReiniciarBase]=None) -> None:
        """
        Refresca el mensaje de la vista.
        """

        await self.mensaje_original.edit(content=mensaje,
                                         view=(self if vista is None else vista))


    async def terminar(self) -> None:
        """
        Trata de terminar la partida.
        """

        if not self.modelo.terminado():
            return

        for mensaje in (self.mensaje_1, self.mensaje_2):
            await mensaje.edit(content=("**¡Ronda terminada!** Vuelve al canal original " +
                                        "para ver el resultado."),
                               delete_after=10.0,
                               view=None)

        # Desde acá las dos elecciones no pueden ser `None`
        msg = (f"**{self.jugador_1.nombre}** eligió `{self.nombre_eleccion_1}`, mientras que " +
               f"**{self.jugador_2.nombre}** eligió `{self.nombre_eleccion_2}`.")
        if self.modelo.empate():
            msg += "\n\n¡El juego terminó en empate!"
            await self.refrescar_mensaje(msg)
        else:
            ganador = self.modelo.determinar_ganador()
            msg += f"\n\n¡El ganador es **{ganador.nombre}**!"
            await self.refrescar_mensaje(msg)

        extra = f"\n\n*¿... otra?*\t**(0 / {self.modelo.cantidad_jugadores})**"
        await self.refrescar_mensaje(mensaje=msg + extra,
                                     vista=ReiniciarPPT(self))


class VistaPPTPrivada(View):
    """
    Vista que sólo ven los jugadores en sus canales privados,
    para no revelar sus elecciones.
    """

    id_piedra: str = "rps_rock"
    id_papel: str = "rps_paper"
    id_tijeras: str = "rps_scissors"

    emojis_por_id: dict[str, str] = {
        id_piedra: EMOJI_PIEDRA,
        id_papel: EMOJI_PAPEL,
        id_tijeras: EMOJI_TIJERAS
    }

    def __init__(self,
                 maestra: VistaPPT,
                 es_primer_jugador: bool):
        """
        Inicializa la vista privada.
        """

        super().__init__(timeout=None)

        self.maestra: VistaPPT = maestra
        self.primer_jugador: bool = es_primer_jugador

        self.elecciones: dict[str, EleccionPPT] = {
            "Piedra": EleccionPPT.PIEDRA,
            "Papel": EleccionPPT.PAPEL,
            "Tijeras": EleccionPPT.TIJERAS
        }

        self.eleccion_str: Optional[str] = None


    @property
    def eleccion(self) -> Optional[EleccionPPT]:
        """
        Elige entre Piedra, Papel o Tijeras según un
        diccionario preparado.
        """

        return self.elecciones.get(self.eleccion_str, None)


    def decidir_func(self) -> DecidirFunc:
        """
        Devuelve, según el jugador, la función que se encarga
        de decidir la elección del mismo.
        """

        if self.primer_jugador:
            return self.maestra.modelo.decidir_1

        return self.maestra.modelo.decidir_2


    def actualizar_botones(self) -> None:
        """
        Actualiza los botones de la vista.
        """

        for item in self.children:
            if not isinstance(item, Button):
                continue

            if item.label == self.eleccion_str:
                item.disabled = True
                item.emoji = Emoji.from_str(CHECKMARK)

            else:
                item.disabled = False
                item.emoji = Emoji.from_str(self.emojis_por_id[item.custom_id])


    async def seguir(self, interaccion: Interaction, boton: Button) -> None:
        """
        Sigue procesando la elección.
        """

        jugador_1, jugador_2 = self.maestra.modelo.jugadores
        jug = (jugador_1 if self.primer_jugador else jugador_2)

        self.eleccion_str = boton.label
        self.decidir_func()(self.eleccion)
        self.maestra.modelo.actualizar()
        if self.primer_jugador:
            self.maestra.nombre_eleccion_1 = self.eleccion_str
        else:
            self.maestra.nombre_eleccion_2 = self.eleccion_str

        self.actualizar_botones()

        await interaccion.response.edit_message(content=f"¡Elegiste **{self.eleccion_str}**!",
                                                view=self)
        await self.maestra.refrescar_mensaje(mensaje=f"¡El jugador **{jug.nombre}** ya decidió!")
        await self.maestra.terminar()


    @button(label="Piedra",
            custom_id=id_piedra,
            style=ButtonStyle.primary,
            emoji=Emoji.from_str(EMOJI_PIEDRA),
            row=0)
    async def eleccion_piedra(self, interaccion: Interaction, boton: Button) -> None:
        """
        El jugador eligió PIEDRA.
        """

        await self.seguir(interaccion, boton)


    @button(label="Papel",
            custom_id=id_papel,
            style=ButtonStyle.primary,
            emoji=Emoji.from_str(EMOJI_PAPEL),
            row=0)
    async def eleccion_papel(self, interaccion: Interaction, boton: Button) -> None:
        """
        El jugador eligió PAPEL.
        """

        await self.seguir(interaccion, boton)


    @button(label="Tijeras",
            custom_id=id_tijeras,
            style=ButtonStyle.primary,
            emoji=Emoji.from_str(EMOJI_TIJERAS),
            row=0)
    async def eleccion_tijeras(self, interaccion: Interaction, boton: Button) -> None:
        """
        El jugador eligió TIJERAS.
        """

        await self.seguir(interaccion, boton)
