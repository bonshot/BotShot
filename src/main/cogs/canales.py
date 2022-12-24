"""
Cog que agrupa comandos para los canales.
"""

from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord.app_commands import Choice, autocomplete, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from ..archivos import cargar_json, guardar_json
from ..auxiliares import autocompletado_todos_canales
from ..constantes import DEV_ROLE_ID, PROPERTIES_FILE
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
        dic_id_guilds = cargar_json(PROPERTIES_FILE).get('canales_escuchables')
        canales = []
        for id_guild, lista_id_canales in dic_id_guilds.items():
            canales_guild = []
            for id_canal in lista_id_canales:
                canales_guild.append(f'**{interaccion.guild.get_channel(int(id_canal)).mention}**:\t`{id_canal}`')
            canales.append(f"**{self.bot.get_guild(int(id_guild)).name}:**\n>>> " + '\n'.join(canales_guild))

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
            canal = str(interaccion.channel.id)
        guild_id = interaccion.guild.id

        dic_propiedades = cargar_json(PROPERTIES_FILE)
        dic_canales = dic_propiedades['canales_escuchables']

        if str(guild_id) not in dic_canales:
            dic_canales[str(guild_id)] = []

        lista_canales = dic_canales[str(guild_id)]
        nombre_canal = interaccion.guild.get_channel(int(canal)).name

        if canal not in lista_canales:
            lista_canales.append(canal)
            dic_propiedades['canales_escuchables'][str(guild_id)] = lista_canales
            guardar_json(dic_propiedades, PROPERTIES_FILE)
            await interaccion.response.send_message(f'Canal `{nombre_canal}` ' +
                                                     'guardado exitosamente en los escuchados!',
                                                    ephemeral=True)
        else:
            await interaccion.response.send_message(f'El canal `{nombre_canal}` ' +
                                                     'ya está agregado, no lo voy a poner de nuevo, crack',
                                                    ephemeral=True)


    @appcommand(name='eliminarch',
                description='Remover un canal al que el bot escucha')
    @describe(canal="El canal a borrar.")
    @choices(canal=[
        Choice(name=canalito, value=canalito)
        for canalito in [ch for sublista in cargar_json(PROPERTIES_FILE).get("canales_escuchables").values()
                         for ch in sublista]
    ])
    @has_role(DEV_ROLE_ID)
    async def eliminar_channel(self, interaccion: Interaction, canal: Choice[str]) -> None:
        """
        Elimina un canal existente en escucha del bot.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        dic_guilds = dic_propiedades['canales_escuchables']
        nombre_canal = interaccion.guild.get_channel(int(canal.value)).name # idealmente canal.name

        for id_guild in dic_guilds:
            if canal in dic_guilds[id_guild]:
                dic_guilds[id_guild].remove(canal.value)
                break

        guardar_json(dic_propiedades, PROPERTIES_FILE)
        await interaccion.response.send_message(f'El canal `{nombre_canal}` fue eliminado exitosamente, pa',
                                                ephemeral=True)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogCanales(bot))
