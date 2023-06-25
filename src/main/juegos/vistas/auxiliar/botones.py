"""
Módulo para botones auxiliares de vistas.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, Union

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ext.tasks import loop
from discord.ui import Button

if TYPE_CHECKING:
    from ...jugador import ListaJugadores
    from ..vista_juego_abc import VistaJuegoBase
    from ..vista_reiniciar_abc import VistaReiniciarBase

VistaMaestra: TypeAlias = Union["VistaReiniciarBase", "VistaJuegoBase"]


class BotonContador(Button, ABC):
    """
    Botón que cuenta cuántos jugadores lo apretaron
    y hace una acción.
    """

    def __init__(self,
                 maestra: VistaMaestra,
                 mensaje: str,
                 mensaje_apretado: Optional[str]=None,
                 cantidad_tope: Optional[int]=None,
                 estilo: ButtonStyle=ButtonStyle.green,
                 custom_id: Optional[str]=None,
                 emoji: Optional[str]=None,
                 row: int=0) -> None:
        """
        Inicia el botón contador.
        """

        self.maestra: VistaMaestra = maestra
        self.mensaje: str = mensaje
        self.mensaje_apretado: str = mensaje_apretado or mensaje
        self.max_cant: int = (cantidad_tope
                              if cantidad_tope is not None
                              else self.maestra.cantidad_jugadores)
        self._jugadores_aceptaron: "ListaJugadores" = []

        super().__init__(style=estilo,
                         label=self.get_mensaje(),
                         disabled=False,
                         custom_id=custom_id,
                         emoji=(Emoji.from_str(emoji)
                                if emoji is not None
                                else emoji),
                         row=row)

        self.realizar_accion.start()


    def __init_subclass__(cls) -> None:
        """
        Cuando se inicia una subclase, crear un diccionario para
        registrar todas las instancias.

        Todas las instancias de esa clase tendrán un único callback.
        """

        cls.accionando: bool = False


    def get_mensaje(self) -> str:
        """
        Devuelve el mensaje actualizado del botón.
        """

        return (f"{self.mensaje} {self._sufijo_msg()}")


    def cambiar_mensaje(self, nuevo_mensaje: str) -> str:
        """
        Cambia el mensaje por otro.
        """

        self.mensaje = nuevo_mensaje
        return self.get_mensaje()


    def _sufijo_msg(self) -> str:
        """
        Sufijo para el mensaje del botón.
        """

        return (f"({self.aceptaciones} / {self.max_cant})")


    def _jugador_acepto(self, id_jugador: str) -> bool:
        """
        Determina por id si un jugador aceptó reiniciar la partida.
        """

        for jugador in self._jugadores_aceptaron:
            if id_jugador == jugador.id:
                return True

        return False


    @property
    def aceptaciones(self) -> int:
        """
        Devuelve cuántos jugadores aceptaron reiniciar la partida.
        """

        return len(self._jugadores_aceptaron)


    def jugador_aceptar(self, id_jugador: str) -> None:
        """
        Un jugador aceptó reiniciar, agregarlo.
        """

        jug = self.maestra.get_jugador(id_jugador)
        self._jugadores_aceptaron.append(jug)


    def jugador_existe(self, id_jugador: str) -> bool:
        """
        Verifica si un jugador existe entre los registrados.

        Esta función se pudede sobrecargar si es necesario.
        """

        return self.maestra.existe_jugador(id_jugador=id_jugador)


    def es_suficiente(self) -> bool:
        """
        Decide si suficientes jugadores aceptaron.

        Esta función se puede sobrecargar de ser necesario.
        """

        return self.aceptaciones >= self.max_cant


    @abstractmethod
    async def accion(self) -> Any:
        """
        Realiza la acción del botón contador.
        """

        raise NotImplementedError


    async def actualizar_vista(self, interaccion: Interaction) -> None:
        """
        Refresca la vista.

        Esta función se puede sobrecargar de ser necesario.
        """

        self.jugador_aceptar(str(interaccion.user.id))
        self.label = self.get_mensaje()
        await interaccion.response.edit_message(view=self.maestra)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Un jugador es agregado al conteo.
        """

        autor = interaccion.user

        if not self.jugador_existe(str(autor.id)):
            msg = f"{autor.mention}, vos no podés apretar este botón."
            await interaccion.response.edit_message(content=msg)
            return


        elif self._jugador_acepto(str(autor.id)):
            msg = f"{autor.mention}, vos ya aceptaste reiniciar la partida."
            await interaccion.response.edit_message(content=msg)
            return

        else:
            self.disabled = True # Sólo se puede apretar una vez
            await self.actualizar_vista(interaccion)


    @loop(seconds=1)
    async def realizar_accion(self) -> None:
        """
        Trata de realizar la acción con varios intentos.
        """

        if not self.es_suficiente():
            return

        self.realizar_accion.stop()


    @realizar_accion.after_loop
    async def despues_loop(self) -> None:
        """
        Realiza definitivamente la acción después de
        acabar el loop.

        La acción sólo se puede hacer una vez.
        """

        cls = type(self)

        if not cls.accionando:
            cls.accionando = True
            await self.accion()
