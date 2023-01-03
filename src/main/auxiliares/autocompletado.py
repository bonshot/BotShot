"""
Módulo para funciones de autocompletado.
"""

from typing import Optional

from discord import ChannelType, Interaction
from discord.app_commands import Choice

from ..archivos import buscar_archivos, partir_ruta
from ..db.atajos import (get_canales_escuchados, get_recomendaciones_carpetas,
                         get_sonidos_path, get_usuarios_autorizados)


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
            if current.lower() in nombre_ch.lower():
                lista_choices.append(Choice(name=nombre_ch, value=str(id_ch)))

    return lista_choices[:25]


async def autocompletado_recomendaciones_carpetas(_interaccion: Interaction,
                                                  current: str) -> list[Choice[str]]:
    """
    Devuelve todas las recomendaciones de carpetas hechas.
    """

    return [Choice(name=recom, value=recom)
            for recom in [dato[0] for dato in get_recomendaciones_carpetas()]
            if current.lower() in recom.lower()
    ][:25]


async def autocompletado_miembros_guild(interaccion: Interaction,
                                        current: str) -> list[Choice[str]]:
    """
    Devuelve todos los usuarios del guild actual.
    """

    return [Choice(name=member.display_name, value=str(member.id))
            for member in interaccion.guild.members
            if (current.lower() in member.name.lower()
                or (current.lower() in member.nick.lower()
                    if member.nick is not None else False))
    ][:25]


async def autocompletado_usuarios_autorizados(_interaccion: Interaction,
                                              current: str) -> list[Choice[str]]:
    """
    Devuelve todos los usuarios autorizados.
    """

    return [Choice(name=f"{nombre}#{discriminador}", value=str(id_usuario))
            for (id_usuario, nombre, discriminador) in get_usuarios_autorizados()
            if current.lower() in nombre.lower()
    ][:25]


async def autocompletado_archivos_audio(_interaccion: Interaction,
                                        current: str) -> list[Choice[str]]:
    """
    Devuelve todos los archivos de audio bajo el directorio
    de sonidos.
    """

    return [
        Choice(name=partir_ruta(ruta)[1], value=ruta)
        for ruta in buscar_archivos(nombre_ruta=get_sonidos_path())
        if current.lower() in ruta.lower()
    ][:25]
