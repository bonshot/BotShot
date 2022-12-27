"""
Cog que agrupa comandos administrativos.
"""

from os import execl
from sys import executable as sys_executable
from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord.app_commands.errors import CheckFailure
from discord.app_commands import AppCommandError, autocomplete
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from discord.ext.commands import Context

from ..auxiliares import (autocompletado_miembros_guild,
                          autocompletado_usuarios_autorizados)
from ..db.atajos import (actualizar_prefijo, borrar_usuario_autorizado,
                         existe_usuario_autorizado, get_log_path,
                         get_prefijo_guild, registrar_usuario_autorizado)
from .cog_abc import GroupsList, _CogABC, _GrupoABC

if TYPE_CHECKING:

    from ..botshot import BotShot


class GrupoAutorizar(_GrupoABC):
    """
    Grupo para comandos de administradores.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia de 'GrupoAutorizar'.
        """

        super().__init__(bot,
                         name="admin",
                         description="Comandos para autorizar usuarios a usar BotShot.")


    async def interaction_check(self, interaccion: Interaction) -> bool:
        """
        Verifica si el usuario está autorizado.
        """

        return ((interaccion.user.id == self.bot.owner_id)
                 or existe_usuario_autorizado(interaccion.user.id))


    async def on_error(self, interaccion: Interaction, error: AppCommandError) -> None:
        """
        Avisa el usuario que un comando falló.
        """

        if isinstance(error, CheckFailure):
            mensaje = f"No no, {interaccion.user.mention}, vos quién sos para autorizar o desautorizar gente?"
            await interaccion.response.send_message(content=mensaje,
                                                    ephemeral=True)
            return

        raise error from error


    @appcommand(name="autorizar",
                description="[ADMIN] Autoriza a un usuario.")
    @describe(usuario="El usuario a autorizar.")
    @autocomplete(usuario=autocompletado_miembros_guild)
    async def agregar_autorizacion(self,
                                   interaccion: Interaction,
                                   usuario: Optional[str]=None) -> None:
        """
        Registra un usuario autorizado.
        """

        if usuario is None:
            usuario = interaccion.user

        else:
            usuario = interaccion.guild.get_member(int(usuario))        

        if registrar_usuario_autorizado(usuario.name, int(usuario.discriminator), usuario.id):
            mensaje = f"Entendido, {usuario.mention}! Ahí te agrego."

        else:
            mensaje = f"Pero, {usuario.mention}, vos ya estás autorizado."

        await interaccion.response.send_message(content=mensaje,
                                                ephemeral=True)

    @appcommand(name="desautorizar",
                description="[ADMIN] Desautoriza a un usuario.")
    @describe(usuario="El usuario a hechar.")
    @autocomplete(usuario=autocompletado_usuarios_autorizados)
    async def sacar_autorizacion(self,
                                 interaccion: Interaction,
                                 usuario: str) -> None:
        """
        Saca del registro a un usuario previamente autorizado.
        """

        id_usuario = int(usuario)
        user = self.bot.get_user(id_usuario)
        borrar_usuario_autorizado(id_usuario)

        await interaccion.response.send_message(f"{user.display_name} fue despejado de todo poder exitosamente.",
                                                ephemeral=True)


class GrupoLog(_GrupoABC):
    """
    Grupos para comandos del logger.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia de 'GrupoLog'.
        """

        super().__init__(bot,
                         name="log",
                         description="Comandos para manejar el logger.")


    async def interaction_check(self, interaccion: Interaction) -> bool:
        """
        Verifica si el usuario está autorizado.
        """

        return ((interaccion.user.id == self.bot.owner_id)
                 or existe_usuario_autorizado(interaccion.user.id))


    async def on_error(self, interaccion: Interaction, error: AppCommandError) -> None:
        """
        Avisa el usuario que un comando falló.
        """

        if isinstance(error, CheckFailure):
            await interaccion.response.send_message((f"Ay, {interaccion.user.mention}, no tenés permiso " +
                                                     "para usar este comando."),
                                                    ephemeral=True)
            return

        raise error from error


    @appcommand(name="flush",
                description="[ADMIN] Vacía el log.")
    async def logflush(self, interaccion: Interaction):
        """
        Vacía el archivo de registros.
        """

        log = get_log_path()

        with open(log, mode='w', encoding="utf-8"):
            await interaccion.response.send_message("**[INFO]** Vaciando el log en " +
                                                    f"`{log}`...",
                                                    ephemeral=True)


class CogAdmin(_CogABC):
    """
    Cog para comandos administrativos.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoAutorizar, GrupoLog]


    def cog_check(self, ctx: Context) -> bool:
        """
        Verifica si el que invoca el comando es un admin o un dev.
        """

        return ((ctx.author.id == self.bot.owner_id)
                 or existe_usuario_autorizado(ctx.author.id))


    async def cog_after_invoke(self, ctx: Context) -> None:
        """
        Borra los mensajes de admin después de un tiempo ejecutado
        el comando.
        """
        await super().cog_after_invoke(ctx)
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
        prefijo_viejo = get_prefijo_guild(guild_id=guild_id)

        if prefijo_viejo == nuevo_prefijo:
            await interaccion.response.send_message(f'Cariño, `{nuevo_prefijo}` *ya es* el prefijo ' +
                                                    'para este server.',
                                                    ephemeral=True)
            return

        actualizar_prefijo(nuevo_prefijo, guild_id)

        await interaccion.response.send_message('**[AVISO]** El prefijo de los comandos fue cambiado de ' +
                                                f'`{prefijo_viejo}` a `{nuevo_prefijo}` exitosamente.',
                                                ephemeral=True)
        self.bot.log.info(f'El prefijo en {interaccion.guild.name!r} fue cambiado de ' +
                          f'{prefijo_viejo!r} a {nuevo_prefijo!r} exitosamente.')


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

        mensaje = f"Reiniciando **{str(self.bot.user)}...**"

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
