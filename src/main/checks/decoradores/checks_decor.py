"""
Módulo para checks decoradores.
"""

from discord import Interaction
from discord.app_commands import check

from ...db.atajos import existe_usuario_autorizado


def es_usuario_autorizado():
    """
    Verifica si el usuario en cuestión está entre
    los autorizados para utilizar comandos admin.
    """

    def predicado(interaccion: Interaction) -> bool:
        """
        Verifica si el usuario está.
        """

        return existe_usuario_autorizado(interaccion.user.id)

    return check(predicado)
