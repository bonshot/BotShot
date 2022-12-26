"""
Cog que agrupa comandos para los canales.
"""

from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord.app_commands import autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from ..auxiliares import (autocompletado_canales_escuchados,
                          autocompletado_todos_canales)
from ..constantes import DEV_ROLE_ID
from ..db.atajos import (actualizar_canal_escuchado, borrar_canal_escuchado,
                         get_canales_escuchados)
from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogCanales(_CogABC):
    """
    Cog para los comandos que interactúan con
    información sobre los canales.
    """

    @appcommand(name='listach',
                description='Mostrar lista de canales que el bot escucha')
    @has_role(DEV_ROLE_ID)
    async def mostrar_channels(self, interaccion: Interaction) -> None:
        """
        Muestra en discord una lista de los canales que el bot está escuchando.
        """
        dic_canales_escuchados = get_canales_escuchados()
        canales = []

        for id_guild, lista_id_canales in dic_canales_escuchados.items():
            canales_guild = []
            for id_canal, _ in lista_id_canales:
                canales_guild.append(f'**{interaccion.guild.get_channel(id_canal).mention}**:\t`{id_canal}`')
            canales.append(f"**{self.bot.get_guild(id_guild).name}:**\n>>> " + '\n'.join(canales_guild))

        mensaje_canales = '\n'.join(canales)
        await interaccion.response.send_message((f'*Lista de Canales Escuchando Actualmente:*\n\n{mensaje_canales}'
                                                 if mensaje_canales else "*Actualmente no hay ningún canal agregado.*"))


    @appcommand(name='agregarch',
                description='Agregar canal al que el bot escucha.')
    @describe(canal='El canal a agregar de este guild a agregar.')
    @has_role(DEV_ROLE_ID)
    @autocomplete(canal=autocompletado_todos_canales)
    async def agregar_channel(self, interaccion: Interaction, canal: Optional[str]=None) -> None:
        """
        Agrega un nuevo canal para que escuche el bot.
        """
        if canal is None:
            canal = interaccion.channel.id
        else:
            canal = int(canal)
        guild_id = interaccion.guild.id
        nombre_canal = interaccion.guild.get_channel(canal).name

        if actualizar_canal_escuchado(id_canal=canal,
                                      nombre_canal=nombre_canal,
                                      id_guild=guild_id):
            await interaccion.response.send_message(f'El canal `{nombre_canal}` ' +
                                                     'ya está presente, pero actualicé el nombre igualmente.',
                                                    ephemeral=True)
        else:
            await interaccion.response.send_message(f'Canal `{nombre_canal}` ' +
                                                     'guardado exitosamente en los escuchados!',
                                                    ephemeral=True)


    @appcommand(name='eliminarch',
                description='Remover un canal al que el bot escucha')
    @describe(canal="El canal a borrar.")
    @autocomplete(canal=autocompletado_canales_escuchados)
    @has_role(DEV_ROLE_ID)
    async def eliminar_channel(self, interaccion: Interaction, canal: str) -> None:
        """
        Elimina un canal existente en escucha del bot.
        """

        nombre_canal = interaccion.guild.get_channel(int(canal)).name
        borrar_canal_escuchado(int(canal))
        await interaccion.response.send_message(f'El canal `{nombre_canal}` fue eliminado exitosamente, pa',
                                                ephemeral=True)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogCanales(bot))
