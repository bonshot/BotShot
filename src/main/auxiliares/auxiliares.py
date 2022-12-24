"""
Módulo para contener funciones auxiliares.
"""

from typing import TYPE_CHECKING, Optional

from discord import ChannelType, Interaction, Message
from discord.app_commands import Choice

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
                                 current: str,
                                 tipos_canales: Optional[tuple[ChannelType, ...]]=None) -> list[Choice[str]]:
    """
    Devuelve todos los canales del guild que coinciden con la búsqueda
    y el tipo actuales.
    """
    canales = interaccion.guild.channels

    return [Choice(name=canal.name, value=str(canal.id)) for canal in canales
            if ((current.lower() in canal.name.lower())
            and (canal.type in tipos_canales if tipos_canales is not None else True))][:20]
    


async def autocompletado_todos_canales(interaccion: Interaction,
                                       current: str) -> list[Choice[str]]:
    """
    Devuelve todos los canales del guild que coinciden con la busqueda actual.
    """
    return await autocompletado_canales(interaccion=interaccion,
                                        current=current)


async def autocompletado_canales_texto(interaccion: Interaction,
                                       current: str) -> list[Choice[str]]:
    """
    Devuelve todos los canales del guild que sean de texto.
    """
    return await autocompletado_canales(interaccion=interaccion,
                                        current=current,
                                        tipos_canales=(ChannelType.text, ))


async def autocompletado_canales_voz(interaccion: Interaction,
                                     current: str) -> list[Choice[str]]:
    """
    Devuelve todos los canales del guild que sean de voz.
    """
    return await autocompletado_canales(interaccion=interaccion,
                                        current=current,
                                        tipos_canales=(ChannelType.voice, ))
        
