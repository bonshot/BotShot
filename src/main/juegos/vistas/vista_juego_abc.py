"""
Vista genérica de un juego.
"""

from typing import TYPE_CHECKING

from discord.ui import View

if TYPE_CHECKING:
    from ...botshot import BotShot
    from ..modelos import JuegoBase


class VistaJuegoBase(View):
    """
    Clase de vista para un juego.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase") -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(timeout=None)

        self.bot: "BotShot" = bot
        self.modelo: "JuegoBase" = modelo
        self.modelo.setup()

