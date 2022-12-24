"""
Cog que agrupa comandos administrativos.
"""

from os import execl
from sys import executable as sys_executable
from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.ext.commands import Context

from ..archivos import cargar_json, guardar_json
from ..constantes import DEV_ROLE_ID, LOG_PATH, PROPERTIES_FILE
from .cog_abc import _CogABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class CogAdmin(_CogABC):
    """
    Cog para comandos administrativos.
    """

    def cog_check(self, ctx: Context) -> bool:
        """
        Verifica si el que invoca el comando es un admin o un dev.
        """

        try:
            return ctx.author.get_role(DEV_ROLE_ID)
        except AttributeError:
            return False


    async def cog_after_invoke(self, ctx: Context) -> None:
        """
        Borra los mensajes de admin después de un tiempo ejecutado
        el comando.
        """
        await ctx.message.delete(delay=5.0)


    @appcommand(name='prefix',
                description='[ADMIN] Cambia el prefijo de los comandos.')
    @describe(nuevo_prefijo="El nuevo prefijo a usar en este servidor.")
    async def cambiar_prefijo(self, interaccion: Interaction, nuevo_prefijo: str) -> None:
        """
        Cambia el prefijo utilizado para convocar a los comandos de texto,
        solamente del servidor de donde este comando fue invocado.
        """
        guild_id = interaccion.guild.id
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        prefijo_viejo = dic_propiedades['prefijos'][str(guild_id)]

        if prefijo_viejo == nuevo_prefijo:
            await interaccion.response.send_message(f'Cariño, `{nuevo_prefijo}` *ya es* el prefijo ' +
                                                    'para este server.',
                                                    ephemeral=True)
            return

        
        dic_propiedades['prefijos'][str(guild_id)] = nuevo_prefijo
        guardar_json(dic_propiedades, PROPERTIES_FILE)

        await interaccion.response.send_message('**[AVISO]** El prefijo de los comandos fue cambiado de ' +
                                                f'`{prefijo_viejo}` a `{nuevo_prefijo}` exitosamente.',
                                                ephemeral=True)
        self.bot.log.info(f'El prefijo en {interaccion.guild.name!r} fue cambiado de ' +
                          f'{prefijo_viejo!r} a {nuevo_prefijo!r} exitosamente.')


    @appcommand(name="flush",
                description="[ADMIN] Vacía el log.")
    async def logflush(self, interaccion: Interaction):
        """
        Vacía el archivo de registros.
        """

        with open(LOG_PATH, mode='w', encoding="utf-8"):
            await interaccion.response.send_message("**[INFO]** Vaciando el log en " +
                                                    f"`{LOG_PATH}`...",
                                                    ephemeral=True)


    async def _desconectar_clientes_de_voz(self) -> None:
        """
        Desconeta BotShot de todas las conexiones de voz que tenga.
        """

        self.bot.log.info("Cerrando conexiones de voz...")

        for client in self.bot.voice_clients:
            await client.disconnect()


    @appcommand(name="reboot",
                description="[ADMIN] Reinicia el bot.")
    async def reboot(self, interaccion: Interaction) -> None:
        """
        Reinicia el bot, apagándolo y volviéndolo a conectar.
        """

        if not sys_executable:

            mensaje = "[ERROR] No se pudo reiniciar el lector."

            await interaccion.response.send_message(content=mensaje,
                                                    ephemeral=True)
            self.bot.log.error(mensaje)
            return

        mensaje = f"Reiniciando bot **{str(self.bot.user)}...**"

        await interaccion.response.send_message(content=mensaje,
                                                ephemeral=True)
        self.bot.log.info(mensaje)

        await self._desconectar_clientes_de_voz()
        execl(sys_executable, sys_executable, "-m", "src.main.main")


    @appcommand(name='shutdown',
                description='[ADMIN] Apaga el Bot.')
    async def apagar_bot(self, interaccion: Interaction) -> None:
        """
        Cierra el Bot de manera correcta.
        """
        adios = "¡Cerrando el Bot!"
        await interaccion.response.send_message(content=adios,
                                                ephemeral=True)
        self.bot.log.info(adios)
        await self._desconectar_clientes_de_voz()
        await self.bot.close()


    @appcommand(name="uptime",
                description="[ADMIN] Calcula el tiempo que BotShot estuvo activo.")
    async def calculate_uptime(self, interaccion: Interaction) -> None:
        """
        Calcula el tiempo de actividad de BotShot.
        """

        delta = self.bot.uptime

        dias = (f"`{delta.days}` día/s" if delta.days > 9 else "")

        horas_posibles = (delta.seconds // 3600)
        horas = (f"`{horas_posibles}` hora/s" if horas_posibles > 0 else "")

        minutos_posibles = (delta.seconds // 60)
        minutos = (f"`{minutos_posibles}` minuto/s" if minutos_posibles > 0 else "")

        segundos_posibles = (delta.seconds % 60)
        segundos = (f"`{segundos_posibles}` segundo/s" if segundos_posibles > 0 else "")

        tiempo = [tmp for tmp in [dias, horas, minutos, segundos] if tmp]
        if len(tiempo) > 1:
            last = tiempo.pop()
            tiempo[-1] = f"{tiempo[-1]} y {last}"


        await interaccion.response.send_message(f"***{self.bot.user}** estuvo activo por " +
                                                f"{', '.join(tiempo)}.*",
                                                ephemeral=True)


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogAdmin(bot))
