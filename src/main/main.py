"""
Módulo principal, wrapper para todos los otros archivos.
Para correr el Bot en sí.
"""

from .botshot import BotShot
from .constantes import BOT_TOKEN


def main() -> int:
    """
    Función principal.
    """

    BotShot().run(BOT_TOKEN)
    return 0


if __name__ == '__main__':
    main()
