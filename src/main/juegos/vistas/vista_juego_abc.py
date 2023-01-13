"""
Vista genérica de un juego.
"""

from typing import TYPE_CHECKING, Optional

from discord.ui import View

if TYPE_CHECKING:
    from ..modelos import JuegoBase


class VistaJuegoBase(View):
    """
    Clase de vista para un juego.
    """

    def __init__(self,
                 modelo: "JuegoBase") -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(timeout=None)

        self.modelo: "JuegoBase" = modelo
        self.modelo.setup()

