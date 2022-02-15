"""
Cog general para uso de herencia.
"""

from discord.ext.commands import Cog, Bot

class CategoriaComandos(Cog):
    """
    Cog general para que se herede de él.
    """

    def __init__(self, bot: Bot) -> None:
        """
        Inicializa una instancia 'CategoriaComandos'.
        """
        self.bot: Bot = bot