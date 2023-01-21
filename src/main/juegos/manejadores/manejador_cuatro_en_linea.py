"""
Módulo para un manejador del 4 en Línea.
"""

from typing import TYPE_CHECKING, Optional

from ..modelos import CuatroEnLinea
from ..opciones import OpcionesCuatroEnLinea
from ..registradores import RegistradorCuatroEnLinea
from ..vistas import VistaCuatroEnLinea, VistaOpcionesCuatroEnLinea
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..opciones import OpcionesBase
    from ..registradores import RegistradorBase
    from ..vistas import VistaJuegoBase, VistaOpcionesBase


class ManejadorCuatroEnLinea(ManejadorBase):
    """
    Clase para manejar un juego de 4 en Línea.
    """

    @staticmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return CuatroEnLinea


    @staticmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
        """
        Devuelve la vista asignado al modelo.
        """

        return VistaCuatroEnLinea


    @staticmethod
    def clase_opciones() -> Optional[type["OpcionesBase"]]:
        """
        Devuelve las opciones del juego, de tenerlas.

        A diferencia del modelo, no es obligatorio tener
        opciones.
        """

        return OpcionesCuatroEnLinea


    @staticmethod
    def clase_vista_opciones() -> Optional["VistaOpcionesBase"]:
        """
        Devuelve la vista de las opciones del juego.
        """

        return VistaOpcionesCuatroEnLinea


    @staticmethod
    def clase_registrador() -> Optional[type["RegistradorBase"]]:
        """
        Devuelve la clase de registrador asociada a este juego.
        """

        return RegistradorCuatroEnLinea
