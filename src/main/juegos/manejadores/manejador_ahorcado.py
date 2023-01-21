"""
Módulo para el manejador del Ahorcado.
"""

from typing import TYPE_CHECKING, Optional

from ..modelos import Ahorcado
from ..opciones import OpcionesAhorcado
from ..vistas import VistaAhorcado, VistaOpcionesAhorcado
from .manejador_abc import ManejadorBase

if TYPE_CHECKING:

    from ..modelos import JuegoBase
    from ..opciones import OpcionesBase
    from ..vistas import VistaJuegoBase, VistaOpcionesBase


class ManejadorAhorcado(ManejadorBase):
    """
    Clase para manejar un juego de Ahorcado.
    """

    @staticmethod
    def clase_modelo() -> type["JuegoBase"]:
        """
        Devuelve el modelo de juego asignado.
        """

        return Ahorcado


    @staticmethod
    def clase_vista_modelo() -> type["VistaJuegoBase"]:
        """
        Devuelve la vista asignado al modelo.
        """

        return VistaAhorcado


    @staticmethod
    def clase_opciones() -> Optional[type["OpcionesBase"]]:
        """
        Devuelve las opciones del juego, de tenerlas.

        A diferencia del modelo, no es obligatorio tener
        opciones.
        """

        return OpcionesAhorcado


    @staticmethod
    def clase_vista_opciones() -> Optional["VistaOpcionesBase"]:
        """
        Devuelve la vista de las opciones del juego.
        """

        return VistaOpcionesAhorcado
