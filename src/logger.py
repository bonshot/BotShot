"""
Módulo que contiene la función creadora del registrador.
"""

import logging

from constantes import LOG_PATH

def nuevo_logger(nombre: str) -> logging.Logger:
    """
    Genera un nuevo registrador.
    """

    formato_mensaje = "[ %(asctime)s ] [ %(levelname)s ] %(message)s"
    formato_fecha = "%d-%m-%Y %H:%M:%S"

    formateador = logging.Formatter(fmt=formato_mensaje, datefmt=formato_fecha)

    archivo_handler = logging.FileHandler(filename=LOG_PATH, encoding="utf-8")
    archivo_handler.setFormatter(formateador)

    consola_handler = logging.StreamHandler()
    consola_handler.setFormatter(formateador)

    log = logging.getLogger(name=nombre)
    log.setLevel(logging.INFO)
    log.addHandler(archivo_handler)
    log.addHandler(consola_handler)

    return log

log = nuevo_logger("BotShot")