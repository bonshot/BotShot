"""
Módulo para los parámetros iniciales de un juego.
"""

from abc import ABC, abstractmethod
from typing import TypeAlias

ListaOpciones: TypeAlias = list["OpcionesBase"]


class OpcionesBase(ABC):
    """
    Clase abstracta para los parámetros y opciones de un modelo
    de juego.
    """

    _ignorar: bool = False

    lista_opciones: ListaOpciones = []


    def __init_subclass__(cls: type["OpcionesBase"]) -> None:
        """
        Registra una subclase.
        """

        if hasattr(cls, "_ignorar") and cls._ignorar is True:
            return

        __class__.lista_opciones.append(cls)


    def __init__(self, mensaje_inicial: str="") -> None:
        """
        Inicializa unas opciones de juego.
        """

        self.mensaje: str = mensaje_inicial


    @abstractmethod
    def propiedades(self) -> list:
        """
        Devuelve una lista de las propiedades de esta clase
        de opciones, apta para procesarlas con un paginador.
        """

        raise NotImplementedError
