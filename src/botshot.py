"""
Módulo dedicado a contener la lógica de una clase que sobrecarga a
'discord.ext.commands.Bot'.
"""

from typing import Callable
from logging import Logger
from discord.ext.commands import Bot

from auxiliares import get_prefijo
from logger import log
from cog_admin import CogAdmin
from cog_eventos import CogEventos
from cog_canales import CogCanales
from cog_imagenes import CogImagenes
from cog_pruebas import CogPruebas
from cog_usuarios import CogUsuarios

# Para que no tire error en Windows al cerrar el Bot.

from platform import system
from asyncio import set_event_loop_policy

try:
    from asyncio import WindowsSelectorEventLoopPolicy
    if system() == "Windows":
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
except ImportError:
    log.warning("No se pudo importar 'WindowsSelectorEventLoopPolicy' al iniciar el Bot, probablemente porque esto no es Windows.")


class BotShot(Bot):
    """
    Clase que sobrecarga al Bot de discord.
    """

    def __init__(self, cmd_prefix: Callable=get_prefijo, **opciones):
        """
        Instancia 'BotShot'.
        """
        super().__init__(cmd_prefix, options=opciones)

        self.add_cog(CogPruebas(self))
        self.add_cog(CogCanales(self))
        self.add_cog(CogAdmin(self))
        self.add_cog(CogUsuarios(self))
        self.add_cog(CogImagenes(self))
        self.add_cog(CogEventos(self))