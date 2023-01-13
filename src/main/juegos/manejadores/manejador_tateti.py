"""
Módulo para un manejador del Tres en Raya.
"""

from typing import TYPE_CHECKING

from ..modelos import TaTeTi
from ..vistas import VistaTaTeTi
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..vistas import VistaJuegoBase


class ManejadorTaTeTi(ManejadorBase):
    """
    Clase para manejar un juego de Tres en Raya.
    """

    @staticmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return TaTeTi


    @staticmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
        """
        Devuelve la vista asignado al modelo.
        """

        return VistaTaTeTi
