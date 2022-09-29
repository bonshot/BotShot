"""
Cog para comandos extras de recomendaciones.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand, choices, Choice
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from ..archivos import cargar_json, guardar_json
from ..constantes import DEV_ROLE_ID, PROPERTIES_FILE
from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogRecomendaciones(_CogABC):
    """
    Cog para comandos de recomendaciones.
    """

    @appcommand(name='recomendar',
                description='Recomienda una nueva carpeta')
    @describe(nombre_carpeta="El nombre del candidato a carpeta.")
    async def recomendar_carpeta(self, interaccion: Interaction, nombre_carpeta: str):
        """
        Agrega un nombre de carpeta a los candidatos de nuevas
        carpetas a agregar.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        if nombre_carpeta not in dic_propiedades['carpetas_recomendadas']:
            dic_propiedades['carpetas_recomendadas'].append(nombre_carpeta)
            guardar_json(dic_propiedades, PROPERTIES_FILE)
            mensaje_a_mostrar = f'La carpeta {nombre_carpeta} fue recomendada rey!'
        else:
            mensaje_a_mostrar = "*Recomendado repetido pa*"

        await interaccion.response.send_message(content=mensaje_a_mostrar,
                                                ephemeral=True)


    @appcommand(name='recomendados',
                description='[ADMIN] Muestra las carpetas recomendadas')
    @has_role(DEV_ROLE_ID)
    async def mostrar_recomendados(self, interaccion: Interaction):
        """
        Muestra una lista de los nombres de carpetas que son candidatos
        a agregar.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        recomendadas = dic_propiedades['carpetas_recomendadas']
        if recomendadas:
            await interaccion.response.send_message(content='>>> \t**Lista de Recomendaciones:**\n\n' +
                                                    '\n'.join(f'\t-\t`{nombre}`' for nombre in recomendadas))
        else:
            await interaccion.response.send_message(content='*No hay recomendaciones crack.*',
                                                    ephemeral=True)


    @appcommand(name='desrecomendar',
                description='[ADMIN] Elimina una de las recomendaciones guardadas.')
    @describe(recomendacion="El nombre de la recomendación guardada.")
    @choices(recomendacion=[
        Choice(name=recom, value=recom) for recom in cargar_json(PROPERTIES_FILE).get("carpetas_recomendadas")
    ])
    @has_role(DEV_ROLE_ID)
    async def borrar_recomendados(self, interaccion: Interaction, recomendacion: Choice[str]) -> None:
        """
        Elimina de los recomendados uno que ya estaba.
        """

        dic_propiedades = cargar_json(PROPERTIES_FILE)
        dic_propiedades["carpetas_recomendadas"].remove(recomendacion.value)
        guardar_json(dic_propiedades, PROPERTIES_FILE)

        await interaccion.response.send_message(content=f"La recomendación `{recomendacion.value}` esa " +
                                                        "la saqué correctamente.")


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogRecomendaciones(bot))
