"""
Vista genérica de un juego.
"""

from typing import TYPE_CHECKING, Any, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ext.tasks import loop
from discord.ui import Button, View

from .auxiliar import cerrar_partida

if TYPE_CHECKING:
    from discord import Message

    from ...botshot import BotShot
    from ...db import CursorDesc
    from ..jugador import Jugador
    from ..modelos import JuegoBase
    from ..registradores import RegistradorBase


class BotonCerrar(Button):
    """
    Botón para cerrar la partida.
    """

    label_normal: str = "Cerrar"
    label_contando: str = "¿Seguro?"
    _cuenta_atras: int = 10

    def __init__(self,
                 maestra: "VistaJuegoBase",
                 id_boton: str,
                 deshabilitar: bool=False) -> None:
        """
        Inicializa el botón para cerrar.
        """

        super().__init__(label=self.label_normal,
                         disabled=deshabilitar,
                         custom_id=id_boton,
                         style=ButtonStyle.gray,
                         emoji=Emoji.from_str("\U0001F6D1"),
                         row=4)

        self.maestra: "VistaJuegoBase" = maestra


    async def refrescar_maestra(self, interaccion: Optional[Interaction]=None) -> None:
        """
        Refresca la vista maestra.
        """

        if interaccion is not None:
            await interaccion.response.edit_message(view=self.maestra)

        else:
            await self.maestra.mensaje_raiz.edit(view=self.maestra)


    @loop(seconds=1, count=_cuenta_atras)
    async def confirmar_cerrar(self) -> None:
        """
        Confirma con una cuenta atrás si el usuario quiere cerrar.
        """

        i = self._cuenta_atras - self.confirmar_cerrar.current_loop
        self.label = f"{self.label_contando} ({i}s)"
        await self.refrescar_maestra()


    @confirmar_cerrar.after_loop
    async def despues_de_cuenta(self) -> None:
        """
        Acciones posteriores a terminar la cuenta.
        """

        self.label = self.label_normal
        await self.refrescar_maestra()


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Cierra la partida.
        """

        if self.confirmar_cerrar.is_running():
            self.confirmar_cerrar.stop()
            await cerrar_partida(interaccion)
        
        else:
            self.confirmar_cerrar.start()
            await self.refrescar_maestra(interaccion)


class VistaJuegoBase(View):
    """
    Clase de vista para un juego.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase",
                 registrador: Optional["RegistradorBase"],
                 mensaje_raiz: Optional["Message"]) -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(timeout=None)

        self.bot: "BotShot" = bot
        self.modelo: "JuegoBase" = modelo
        self.registrador: Optional["RegistradorBase"] = registrador
        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        if self.agregar_boton_cerrar():
            self.boton_cerrar: BotonCerrar = BotonCerrar(self,
                                                         self.get_cerrar_id(),
                                                         self.deshabilitar_boton_cerrar())
            self.add_item(self.boton_cerrar)

        self.modelo.setup()


    async def on_timeout(self) -> None:
        """
        Pasó el tiempo.
        """

        self.clear_items()
        if self.mensaje_raiz is not None:
            await self.mensaje_raiz.edit(content="*Tiempo agotado. Cerrando...*",
                                         delete_after=5.0)


    async def setup(self) -> None:
        """
        Acciones a realizar justo al inciarse la partida, NO
        al inicializarse la instancia junto con el manejador.

        Por default no hace nada.
        """

        return


    def clonar(self) -> "VistaJuegoBase":
        """
        Devuelve una copia, reiniciada del mismo.
        """

        return type(self)(self.bot,
                          self.modelo,
                          self.registrador,
                          self.mensaje_raiz)


    @staticmethod
    def agregar_boton_cerrar() -> bool:
        """
        Decide si agregar un botón para cerrar la vista.

        Subclases pueden sobreescribir esto para cambiarlo.
        """

        return True


    @staticmethod
    def deshabilitar_boton_cerrar() -> bool:
        """
        Si el botón de cerrar debería iniciar deshabilitado o no.
        """

        return False


    @staticmethod
    def get_cerrar_id() -> str:
        """
        El ID del botón para cerrar la vista.
        """

        return "game_close"


    @property
    def cantidad_jugadores(self) -> int:
        """
        Devuelve la cantidad de jugadores.
        """

        return self.modelo.cantidad_jugadores


    def existe_jugador(self, *, id_jugador: str) -> bool:
        """
        Basado en el id de un jugador, decide si el pasado está
        entre los jugadores actuales.
        """

        return self.modelo.existe_jugador(id_jugador=id_jugador)


    def get_jugador(self, id_jugador: str) -> Optional["Jugador"]:
        """
        Devuelve un jugador unido según el ID, si lo encuentra.

        Sino devuelve `None`.
        """

        return self.modelo.get_jugador(id_jugador)


    def refrescar_datos(self, *, id_jugador: str, **kwargs) -> "CursorDesc":
        """
        Refresca los datos como las estadísticas
        en la DB.
        """

        if self.registrador is not None:
            self.registrador.refrescar_datos(id_jugador=id_jugador, **kwargs)
