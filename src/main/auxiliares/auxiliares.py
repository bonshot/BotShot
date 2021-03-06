"""
Módulo para contener funciones auxiliares.
"""

from typing import TYPE_CHECKING

from discord import Message
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


def conseguir_id_canal(ctx: Context) -> int:
    """
    Si el mensaje tiene menciones a un canal, devuelve el id de la primera
    de esas menciones, caso contario devuelve el canal sobre el que está parado.
    """
    menciones_canales = ctx.message.channel_mentions

    if menciones_canales:
        return menciones_canales[0].id
    return ctx.channel.id
