"""
Cog que agrupa comandos para interactuar con la DB.
"""

from sqlite3 import OperationalError
from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import Choice, autocomplete, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.app_commands.errors import AppCommandError, CheckFailure

from ...auxiliares import autocompletado_nombres_tablas_db
from ...db import (actualizar_dato_de_tabla, borrar_datos_de_tabla,
                   ejecutar_linea, existe_dato_en_tabla,
                   insertar_datos_en_tabla, sacar_datos_de_tabla)
from ..cog_abc import GroupsList, _CogABC, _GrupoABC

if TYPE_CHECKING:
    from ...botshot import BotShot


class GrupoDB(_GrupoABC):
    """
    Grupo para comandos que ejecutan comandos de SQLite3.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia de 'GrupoDB'.
        """

        super().__init__(bot,
                         name="db",
                         description="Comandos para ejecutar comandos a la DB.")


    async def interaction_check(self, interaccion: Interaction) -> bool:
        """
        Verifica si el usuario está autorizado.
        """

        return self.bot.es_admin(interaccion.user.id)


    async def on_error(self, interaccion: Interaction, error: AppCommandError) -> None:
        """
        Avisa el usuario que un comando falló.
        """

        if isinstance(error, CheckFailure):
            mensaje = f"Nope, {interaccion.user.mention}, vos no podés tocar la base de datos "
            await interaccion.response.send_message(content=mensaje,
                                                    ephemeral=True)
            return

        raise error from error


    @appcommand(name="linea",
                description="Ejecuta una operación de una línea.")
    @describe(comando="El comando a ejecutar. Debe obedecer la sintaxis de SQLite3.")
    async def ejecutarlinea(self, interaccion: Interaction, comando: str) -> None:
        """
        Ejecuta un comando de una línea.
        """

        ejecutar_linea(comando=comando)
        await interaccion.response.send_message(f"Ejecutando `{comando}`...",
                                                ephemeral=True)

    @appcommand(name="fetch",
                description="Saca un dato de una tabla.")
    @describe(tabla="La tabla de donde sacar datos.",
              condiciones=("Las condiciones deben venir en el formato " +
                           "'prop1=val1 -- prop2=val2 -- ...'"),
              sacar_uno="Si sacar sólo un resultado o todos.")
    @choices(sacar_uno=[
        Choice(name="Uno solo", value=1),
        Choice(name="Todos", value=0)
    ])
    @autocomplete(tabla=autocompletado_nombres_tablas_db)
    async def dbfetch(self,
                      interaccion: Interaction,
                      tabla: str,
                      condiciones: str,
                      sacar_uno: Choice[int]=0) -> None:
        """
        Saca datos de una tabla.
        """

        try:
            conds_strs = ''.join(condiciones.split()).split("--")
            conds = {}
            for cond in conds_strs:
                if not cond: # Un string vacío
                    continue

                prop, val = cond.split("=")
                conds[eval(prop)] = eval(val)

            res = sacar_datos_de_tabla(tabla=tabla,
                                    sacar_uno=bool(sacar_uno),
                                    **conds)
            res_msg = ">>> " + "\n".join([f"- `{str(r)}`" for r in res])
        except SyntaxError:
            res_msg = "**[ERROR]** `/db fetch`: *Sintaxis inválida.*"
        except OperationalError as e:
            res_msg = f"**[ERROR]** `/db fetch`: *{str(e)!r}*"

        await interaccion.response.send_message(content=(res_msg
                                                        if res_msg
                                                        else "*No se encontró nada.*"),
                                                ephemeral=True)


class CogDB(_CogABC):
    """
    Cog para comandos de DB.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoDB]


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogDB(bot))
