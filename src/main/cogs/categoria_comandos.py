"""
Cog general para uso de herencia.
"""

from typing import TYPE_CHECKING

from discord.ext.commands import Cog

if TYPE_CHECKING:

    from ..botshot import BotShot


class CategoriaComandos(Cog):
    """
    Cog general para que se herede de él.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia 'CategoriaComandos'.
        """
        self.bot: "BotShot" = bot
