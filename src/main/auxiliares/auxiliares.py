"""
Módulo para contener funciones auxiliares.
"""

from typing import TYPE_CHECKING

from discord import Message

from ..db.atajos import get_prefijo_guild

if TYPE_CHECKING:

    from ..botshot import BotShot


def get_prefijo(_bot: "BotShot", mensaje: Message) -> str:
    """
    Se fija en el diccionario de prefijos y devuelve el que
    corresponda al servidor de donde se convoca el comando.
    """

    return get_prefijo_guild(guild_id=mensaje.guild.id)
