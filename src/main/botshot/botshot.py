"""
Módulo dedicado a contener la lógica de una clase que sobrecarga a
'discord.ext.commands.Bot'.
"""

from asyncio import set_event_loop_policy
from platform import system
from typing import Any, Callable, Dict

from discord import Intents, Message
from discord.ext.commands import Bot

from ..archivos import get_nombre_archivos
from ..auxiliares import get_prefijo
from ..constantes import BOT_ID, COGS_PATH
from ..logger import BotLogger

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

        intents = Intents.default()
        intents.message_content = True # pylint: disable=assigning-non-slot

        return intents


    def __init__(self,
                 cmd_prefix: PrefixCallable=get_prefijo,
                 **opciones) -> None:
        """
        Inicializa una instancia de 'BotShot'.
        """
        super().__init__(cmd_prefix,
                         intents=BotShot.intents_botshot(),
                         application_id=BOT_ID,
                         options=opciones)

        self.partidas_truco: Dict[str, Any] = {}


    async def setup_hook(self) -> None:
        """
        Reliza acciones iniciales que el bot necesita.
        """

        ext = "py"

        for cog_name in get_nombre_archivos(COGS_PATH, ext=ext):
            if cog_name == "__init__.py":
                continue

            await self.load_extension(f".{cog_name.removesuffix(f'.{ext}')}",
                                      package="src.main.cogs")

        await self.tree.sync()


    @property
    def log(self) -> BotLogger:
        """
        Devuelve el logger asignado a botshot.
        """

        return BotLogger()
