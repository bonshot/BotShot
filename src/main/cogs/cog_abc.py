"""
Cog general para uso de herencia.
"""

from typing import TYPE_CHECKING

from discord.ext.commands import Cog

if TYPE_CHECKING:

    from ..botshot import BotShot


class _CogABC(Cog):
    """
    Cog general para que se herede de él.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia '_CogABC', o una hija.
        """
        self.bot: "BotShot" = bot


async def setup(bot: "BotShot"):
    """
    Esta función está sólo por compatibilidad. No hace nada.
    """
    ...
