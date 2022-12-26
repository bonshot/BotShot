"""
Cog para comandos extras de recomendaciones.
"""

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.checks import has_role

from ..constantes import DEV_ROLE_ID
from ..auxiliares import autocompletado_recomendaciones_carpetas
from ..db.atajos import (borrar_recomendacion_carpeta,
                         get_recomendaciones_carpetas,
                         insertar_recomendacion_carpeta)
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
        if insertar_recomendacion_carpeta(nombre_carpeta=nombre_carpeta,
                                          nombre_usuario=interaccion.user.name,
                                          id_usuario=interaccion.user.id):
            mensaje_a_mostrar = f'La carpeta `{nombre_carpeta}` fue recomendada rey!'

        else:
            mensaje_a_mostrar = "*Vos ya recomendaste esa pa.*"

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

        recomendadas = get_recomendaciones_carpetas()

        if recomendadas:
            contenido = ('>>> \t**Lista de Recomendaciones:**\n\n' +
                         '\n'.join(f'\t-\t`{nombre_f}`\t( *{self.bot.get_user(id_u)}* )' for (nombre_f, _, id_u) in recomendadas))
        else:
            contenido = '*No hay recomendaciones crack.*'

        await interaccion.response.send_message(content=contenido,
                                                ephemeral=True)


    @appcommand(name='desrecomendar',
                description='[ADMIN] Elimina una de las recomendaciones guardadas.')
    @describe(recomendacion="El nombre de la recomendación guardada.")
    @autocomplete(recomendacion=autocompletado_recomendaciones_carpetas)
    @has_role(DEV_ROLE_ID)
    async def borrar_recomendados(self, interaccion: Interaction, recomendacion: str) -> None:
        """
        Elimina de los recomendados uno que ya estaba.
        """

        borrar_recomendacion_carpeta(recomendacion)

        await interaccion.response.send_message(content=f"La recomendación `{recomendacion}` esa " +
                                                        "la saqué correctamente.")


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogRecomendaciones(bot))
