"""
Módulo principal, wrapper para todos los otros archivos.
Para correr el Bot en sí.
"""

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

from botshot import BotShot

def main():

    BotShot().run(TOKEN)
    return 0


if __name__ == '__main__':
    main()
