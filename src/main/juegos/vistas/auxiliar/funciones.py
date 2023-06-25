"""
Módulo para funciones auxiliares de vistas.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Interaction

async def cerrar_partida(interaccion: "Interaction") -> None:
    """
    Función auxiliar para cerrar una partida.
    """

    await interaccion.message.delete()
    await interaccion.response.send_message(content="*Terminando partida...*",
                                            delete_after=5.0)
