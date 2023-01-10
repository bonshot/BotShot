"""
Cog para tareas periódicas, como loops.
"""

from typing import TYPE_CHECKING

from discord.ext.tasks import loop

from ...archivos import hacer_backup_db
from ..cog_abc import _CogABC

if TYPE_CHECKING:

    from discord.ext.tasks import Loop

    from ...botshot import BotShot


class CogTareas(_CogABC):
    """
    Cog para loops y demás.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instancia '_CogABC', o una hija.
        """

        super().__init__(bot)

        self.tareas: list["Loop"] = [
            self.backup_db
        ]

        self.iniciar_tareas()


    def iniciar_tareas(self) -> None:
        """
        Inicia todas las tareas.
        """

        self.bot.log.info("Iniciando tareas...")
        for tarea in self.tareas:
            tarea.start()


    async def cog_unload(self) -> None:
        """
        Procedimientos finales antes de cerrar el cog.
        """

        self.bot.log.info("Cancelando tareas...")
        for tarea in self.tareas:
            tarea.cancel()


    @loop(hours=24.0)
    async def backup_db(self) -> None:
        """
        Hace un backup de la DB.
        """

        hacer_backup_db()


    @backup_db.before_loop
    async def wait_for_bot(self) -> None:
        """
        Espera hasta que el bot esté listo.
        """

        await self.bot.wait_until_ready()


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogTareas(bot))
