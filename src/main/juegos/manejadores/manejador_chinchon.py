"""
Módulo para el manjeador del Chinchón.
"""

from typing import TYPE_CHECKING, Optional

from ..modelos import Chinchon
from ..vistas import VistaChinchon
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..opciones import OpcionesBase
    from ..registradores import RegistradorBase
    from ..vistas import VistaJuegoBase, VistaOpcionesBase


class ManejadorChinchon(ManejadorBase):
    """
    Clase para manejar un juego de Tres en Raya.
    """

    @staticmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return Chinchon

    @staticmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
        """
        Devuelve la vista asignado al modelo.
        """

        return VistaChinchon


    @staticmethod
    def clase_opciones() -> Optional[type["OpcionesBase"]]:
        """
        Devuelve las opciones del juego, de tenerlas.

        A diferencia del modelo, no es obligatorio tener
        opciones.
        """

        return None


    @staticmethod
    def clase_vista_opciones() -> Optional["VistaOpcionesBase"]:
        """
        Devuelve la vista de las opciones del juego.
        """

        return None


    @staticmethod
    def clase_registrador() -> Optional[type["RegistradorBase"]]:
        """
        Devuelve la clase de registrador asociada a este juego.
        """

        return None
