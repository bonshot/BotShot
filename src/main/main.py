"""
Módulo principal, wrapper para todos los otros archivos.
Para correr el Bot en sí.
"""

from os import getenv

from dotenv import load_dotenv

from .botshot import BotShot

load_dotenv()


def main() -> int:
    """
    Función principal.
    """

    BotShot().run(getenv('TOKEN'))
    return 0


if __name__ == '__main__':
    main()
