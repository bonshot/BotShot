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

from ..archivos import lista_archivos
from ..auxiliares import get_prefijo
from ..db.atajos import get_botshot_id, get_cogs_path, actualizar_guild
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

        self.despierto_desde: "datetime" = utcnow()


    async def setup_hook(self) -> None:
        """
        Reliza acciones iniciales que el bot necesita.
        """

        ext = "py"

        for cog_name in lista_archivos(get_cogs_path(), ext=ext):
            if cog_name == "__init__.py":
                continue

            await self.load_extension(f".{cog_name.removesuffix(f'.{ext}')}",
                                      package="src.main.cogs")

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
    def log(self) -> BotLogger:
        """
        Devuelve el logger asignado a botshot.
        """

        return BotLogger()


    @property
    def uptime(self) -> "timedelta":
        """
        Shows Botarius' uptime.
        """

        return utcnow() - self.despierto_desde
