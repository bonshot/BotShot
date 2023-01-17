"""
Cog para manejar comandos de juegos.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from emoji import is_emoji

from ...db.atajos import (actualizar_emoji_de_jugador,
                          actualizar_nombre_de_jugador)
from ...interfaces import SelectorJuegos
from ...juegos import LONGITUD_MAXIMA_NOMBRE
from ..cog_abc import GroupsList, _CogABC, _GrupoABC

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
    async def init_diversion(self, interaccion: Interaction) -> None:
        """
        Inicia algún juego.
        """

        await interaccion.response.send_message(content="*Iniciando menu...*",
                                                ephemeral=True)

        await interaccion.channel.send(content="Por favor elige un juego:",
                                       view=SelectorJuegos(self.bot))


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogJuegos(bot))
