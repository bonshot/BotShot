"""
Módulo para contener los distintos tipos de palos de una carta.
"""

from enum import Enum


class Palo(Enum):
    """
    Posible palo de una carta.
    """

    ESPADA = "Espada"
    ORO = "Oro"
    COPA = "Copa"
    BASTO = "Basto"
    COMODIN = "Comodin"
