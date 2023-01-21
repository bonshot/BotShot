"""
Módulo para un manejador del Piedra, Papel o Tijeras.
"""

from typing import TYPE_CHECKING, Optional

from ..modelos import PPT
from ..registradores import RegistradorPPT
from ..vistas import VistaPPT
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..registradores import RegistradorBase
    from ..vistas import VistaJuegoBase


class ManejadorPPT(ManejadorBase):
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


    @staticmethod
    def clase_registrador() -> Optional[type["RegistradorBase"]]:
        """
        Devuelve la clase de registrador asociada a este juego.
        """

        return RegistradorPPT
