"""
Módulo dedicado a contener la lógica de una clase que sobrecarga a
'discord.ext.commands.Bot'.
"""

from asyncio import set_event_loop_policy
from platform import system
from typing import TYPE_CHECKING, Callable

from discord import Intents, Message
from discord.ext.commands import Bot
from discord.utils import utcnow

from ..archivos import buscar_archivos
from ..auxiliares import get_prefijo
from ..db.atajos import (actualizar_guild, existe_usuario_autorizado,
                         get_botshot_id, get_cogs_path)
from ..logger import BotLogger

if TYPE_CHECKING:
    from datetime import datetime, timedelta

# Para que no tire error en Windows al cerrar el Bot.

try:
    from asyncio import \
        WindowsSelectorEventLoopPolicy  # pylint: disable=ungrouped-imports
    if system() == "Windows":
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
except ImportError:
    BotLogger().warning("No se pudo importar 'WindowsSelectorEventLoopPolicy' al iniciar " +
                        "el Bot, probablemente porque esto no es Windows.")


PrefixCallable = Callable[["BotShot", Message], str]


# pylint: disable=abstract-method
class BotShot(Bot):
    """
    Clase que sobrecarga al Bot de discord.
    """

    @staticmethod
    def intents_botshot() -> Intents:
        """
        Devuelve los intents específicos para BotShot.
        """

        return Intents.all()


    def __init__(self,
                 cmd_prefix: PrefixCallable=get_prefijo,
                 **opciones) -> None:
        """
        Inicializa una instancia de 'BotShot'.
        """
        super().__init__(cmd_prefix,
                         intents=BotShot.intents_botshot(),
                         application_id=get_botshot_id(),
                         options=opciones)

        self.log: BotLogger = BotLogger()
        self.despierto_desde: "datetime" = utcnow()


    async def setup_hook(self) -> None:
        """
        Reliza acciones iniciales que el bot necesita.
        """

        await self.cargar_cogs()


    async def cargar_cogs(self) -> None:
        """
        Busca y carga recursivamente todos los cogs
        del bot.
        """

        ext = "py"

        for ruta_cog in buscar_archivos(patron=f"*.{ext}",
                                        nombre_ruta=get_cogs_path(),
                                        ignorar_patrones=("__init__.*", "*_abc.*")):

            self.log.info(f"[COG] Cargando cog {ruta_cog!r}")
            await self.load_extension(ruta_cog.removesuffix(f".{ext}").replace("/", "."))

        self.log.info("Sincronizando arbol de comandos...")
        await self.tree.sync()


    def actualizar_db(self) -> None:
        """
        Hace todos los procedimientos necesarios para actualizar
        la base de datos de ser necesario.
        """

        self.log.info("[DB] Actualizando guilds...")
        for guild in self.guilds:
            actualizar_guild(guild.id, guild.name)


    @property
    def uptime(self) -> "timedelta":
        """
        Shows Botarius' uptime.
        """

        return utcnow() - self.despierto_desde


    def es_admin(self, user_id: int) -> bool:
        """
        Verifica si el id de un usuario pertenece al
        de uno autorizado a usar BotShot.
        """

        return (user_id == self.owner_id
                or existe_usuario_autorizado(user_id))
