"""
Cog para manejar comandos de juegos.
"""

from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord.app_commands import autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from emoji import is_emoji

from ...db.atajos import (actualizar_emoji_de_jugador,
                          actualizar_nombre_de_jugador)
from ...interfaces import SelectorJuegos
from ...juegos import LONGITUD_MAXIMA_NOMBRE
from ...juegos.manejadores import ManejadorBase
from ..cog_abc import GroupsList, _CogABC, _GrupoABC
from ...auxiliares import autocompletado_nombres_manejadores

if TYPE_CHECKING:

    from ...botshot import BotShot


class GrupoJugador(_GrupoABC):
    """
    Grupo para comandos que interactúan con objetos 'Jugador'.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instacia de 'GrupoJugador'.
        """

        super().__init__(bot,
                         name="jugador",
                         description="Comandos para interactuar con jugadores.")


    def _es_convertible(self, emoji: str) -> bool:
        """
        Define si un string es convertible al formato 'U+XXXX'.
        """

        try:
            f"{ord(emoji):X}"
        except:
            return False
        else:
            return True


    @appcommand(name="nombre",
                description="Cambiar el nombre del jugador asociado.")
    @describe(nuevo_nombre="El nuevo nombre a utilizar.")
    async def cambiar_nombre(self, interaccion: Interaction, nuevo_nombre: str) -> None:
        """
        Cambia el nombre de un jugador.
        """

        if len(nuevo_nombre) > LONGITUD_MAXIMA_NOMBRE:
            msg = (f"**Nombre `{nuevo_nombre}` no permitido.** Debe tener como máximo " +
                   f"{LONGITUD_MAXIMA_NOMBRE} caracteres.")
            await interaccion.response.send_message(content=msg,
                                                    ephemeral=True)
            return

        autor = interaccion.user

        actualizar_nombre_de_jugador(id_jugador=str(autor.id),
                                     nuevo_nombre=autor.display_name,)
        msg = f"*Nombre cambiado a* `{nuevo_nombre}` *correctamente.*"
        await interaccion.response.send_message(content=msg,
                                                ephemeral=True)


    @appcommand(name="emoji",
                description="Cambiar el emoji del jugador asociado.")
    @describe(nuevo_emoji="El nuevo emoji a utilizar.")
    async def cambiar_emoji(self, interaccion: Interaction, nuevo_emoji: str) -> None:
        """
        Cambia el emoji de un jugador.
        """

        if not self._es_convertible(nuevo_emoji):
            msg = "*Yo no puedo usar ese emoji.*"

        elif not is_emoji(nuevo_emoji):
            msg = "*Emoji no válido.*"

        else:
            msg = f"*Emoji cambiado a* `{nuevo_emoji}` *correctamente.*"
            codepoint = f"U+{ord(nuevo_emoji):X}" # U+XXXX
            actualizar_emoji_de_jugador(str(interaccion.user.id), codepoint)

        await interaccion.response.send_message(content=msg,
                                                ephemeral=True)


class CogJuegos(_CogABC):
    """
    Cog para comandos de manejar juegos.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoJugador]


    @appcommand(name="jugar",
                description="Inicia una partida de algún juego.")
    @describe(juego="El juega a iniciar.")
    @autocomplete(juego=autocompletado_nombres_manejadores)
    async def init_diversion(self, interaccion: Interaction, juego: Optional[str]) -> None:
        """
        Inicia algún juego.
        """

        if juego is None:
            await interaccion.response.send_message(content="Por favor elige un juego:",
                                                    ephemeral=True,
                                                    view=SelectorJuegos(self.bot))
            return

        for manejador in ManejadorBase.lista_clases_manejadores:
            if juego == manejador.nombre_juego():
                await SelectorJuegos.iniciar_lobby(clase_manejador=manejador,
                                                   interaccion=interaccion,
                                                   bot=self.bot,
                                                   editar=False)
                break


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogJuegos(bot))
