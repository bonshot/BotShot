"""
Módulo para enumeraciones.
"""

from enum import Enum

class RestriccionesSonido(Enum):
    """
    Tipos de restricciones para subir un sonido
    personalizado.
    """

    MUY_PESADO = "Tamaño demasiado grande"
    DEMASIADO_LARGO = "Duración demasiada larga"
