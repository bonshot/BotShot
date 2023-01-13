"""
Módulo para los parámetros iniciales de un juego.
"""

from abc import ABC
from typing import TypeAlias

ListaOpciones: TypeAlias = list["OpcionesBase"]


class OpcionesBase(ABC):
    """
    Clase abstracta para los parámetros y opciones de un modelo
    de juego.
    """
