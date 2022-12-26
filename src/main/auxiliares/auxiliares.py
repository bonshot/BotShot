"""
Módulo para contener funciones auxiliares.
"""

from typing import TYPE_CHECKING, Optional

from discord import ChannelType, Interaction, Message
from discord.app_commands import Choice

from ..db.atajos import get_canales_escuchados, get_prefijo_guild, get_recomendaciones_carpetas

if TYPE_CHECKING:

    from ..botshot import BotShot


def get_prefijo(_bot: "BotShot", mensaje: Message) -> str:
    """
    Se fija en el diccionario de prefijos y devuelve el que
    corresponda al servidor de donde se convoca el comando.
    """

    return get_prefijo_guild(guild_id=mensaje.guild.id)


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
            and (canal.type in tipos_canales if tipos_canales is not None else True))][:25]
    


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


async def autocompletado_canales_escuchados(_interaccion: Interaction,
                                            current: str) -> list[Choice[str]]:
    """
    Devuelve todos los canales escuchados por BotShot.
    """

    lista_choices = []

    for lista_ch in get_canales_escuchados().values():
        for id_ch, nombre_ch in lista_ch:
            if current in nombre_ch:
                lista_choices.append(Choice(name=nombre_ch, value=str(id_ch)))

    return lista_choices[:25]


async def autocompletado_recomendaciones_carpetas(_interaccion: Interaction,
                                                  current: str) -> list[Choice[str]]:
    """
    Devuelve todas las recomendaciones de carpetas hechas.
    """

    return [Choice(name=recom, value=recom)
            for recom in [dato[0] for dato in get_recomendaciones_carpetas()]
            if current in recom
    ][:25]
