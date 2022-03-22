"""
Módulo dedicado a contener la lógica de una clase que sobrecarga a
'discord.ext.commands.Bot'.
"""

from asyncio import set_event_loop_policy
from platform import system
from typing import Any, Callable, Dict

from discord import Message
from discord.ext.commands import Bot

from ..auxiliares import get_prefijo
from ..cogs import (CogAdmin, CogCanales, CogEventos, CogImagenes, CogPruebas,
                    CogUsuarios)
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


    def __init__(self, cmd_prefix: PrefixCallable=get_prefijo, **opciones):
        """
        Instancia 'BotShot'.
        """
        super().__init__(cmd_prefix, options=opciones)

        self.add_cog(CogPruebas(self))
        self.add_cog(CogCanales(self))
        self.add_cog(CogAdmin(self))
        self.add_cog(CogUsuarios(self))
        self.add_cog(CogImagenes(self))
        self.add_cog(CogEventos(self))

        self.partidas_truco: Dict[str, Any] = {}


    @property
    def log(self) -> BotLogger:
        """
        Devuelve el logger asignado a botshot.
        """

        return BotLogger()
