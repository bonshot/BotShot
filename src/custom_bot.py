"""
Módulo dedicado a contener la lógica de una clase que sobrecarga a
'discord.ext.commands.Bot'.
"""

import logging

from typing import Callable
from discord import Message
from discord.ext.commands import Bot

import archivos

from constantes import PREFIXES_FILE, DEFAULT_PREFIX, LOG_PATH

def nuevo_logger(nombre: str) -> logging.Logger:
    """
    Genera un nuevo registrador.
    """

    formato_mensaje = "[ %(asctime)s ] - %(levelname)s - %(message)s"
    formato_fecha = "%d-%m-%Y %H:%M:%S"

    formateador = logging.Formatter(fmt=formato_mensaje, datefmt=formato_fecha)

    archivo_handler = logging.FileHandler(filename=LOG_PATH, encoding="utf-8")
    archivo_handler.setFormatter(formateador)

    consola_handler = logging.StreamHandler()
    consola_handler.setFormatter(formateador)

    log = logging.getLogger(name=nombre)
    log.setLevel(logging.INFO)
    log.addHandler(consola_handler)

    return log

log = nuevo_logger("BotShot")

def get_prefijo(bot, mensaje: Message) -> str:
    """
    Se fija en el diccionario de prefijos y devuelve el que
    corresponda al servidor de donde se convoca el comando.
    """

    return archivos.cargar_pares_valores(PREFIXES_FILE).get(str(mensaje.guild.id), DEFAULT_PREFIX)


class CustomBot(Bot):
    """
    Clase que sobrecarga al Bot de discord.
    """

    def __init__(self, cmd_prefix: Callable=get_prefijo, **opciones):
        """
        Instancia 'CustomBot'.
        """

        super().__init__(cmd_prefix, options=opciones)
