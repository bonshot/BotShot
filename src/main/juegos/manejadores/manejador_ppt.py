"""
Módulo para un manejador del Piedra, Papel o Tijeras.
"""

from typing import TYPE_CHECKING

from ..modelos import PPT
from ..vistas import VistaPPT
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..vistas import VistaJuegoBase


class ManejadorTaTeTi(ManejadorBase):
    """
    Clase para manejar un juego de Piedra, Papel o Tijeras.
    """

    @staticmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return PPT


    @staticmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
        """
        Devuelve la vista asignado al modelo.
        """

        return VistaPPT
