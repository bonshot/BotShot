"""
Módulo para almacenar constantes.
"""

from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('TOKEN')
"""
El token usado para logear el bot.
"""

BOT_VERSION = "0.1.0"
"""
La versión de BotShot.
"""

BOT_ID = 839702615977492510
"""
El ID único de BotShot.
"""

DEFAULT_PREFIX = '.'
"""
El prefijo por defecto, que se asigna cuando el bot ingresa
por primera vez a un server o cuando no es válida la opción querida.
"""

DEV_ROLE_ID = 925517040993861654
"""
Rol de Discord específico para los desarrolladores de BotShot.
"""

PROPERTIES_FILE = 'src/main/json/propiedades.json'

STATS_FILE = 'src/main/json/stats.json'

IMAGES_PATH = 'images'

COGS_PATH = "src/main/cogs"

LOG_PATH = 'botshot.log'
