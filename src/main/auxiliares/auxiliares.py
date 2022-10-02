"""
Módulo para contener funciones auxiliares.
"""

from typing import TYPE_CHECKING, Iterable

from discord import Interaction, Message
from discord.app_commands import Choice
from discord.ext.commands import Context

from ..archivos import cargar_json
from ..constantes import DEFAULT_PREFIX, PROPERTIES_FILE

if TYPE_CHECKING:

    from ..botshot import BotShot


def get_prefijo(_bot: "BotShot", mensaje: Message) -> str:
    """
    Se fija en el diccionario de prefijos y devuelve el que
    corresponda al servidor de donde se convoca el comando.
    """

    return cargar_json(PROPERTIES_FILE).get("prefijos").get(str(mensaje.guild.id), DEFAULT_PREFIX)


async def autocompletado_canales(interaccion: Interaction,
                                 current: str) -> list[Choice[str]]:
        """
        Devuelve todos los canales del guild que coinciden con la busqueda actual.
        """

        canales = interaccion.guild.channels

        return [Choice(name=canal.name, value=str(canal.id)) for canal in canales
                if current.lower() in canal.name.lower()]
