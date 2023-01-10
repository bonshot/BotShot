"""
Módulo para algoritmos de backup.
"""

from datetime import datetime
from zipfile import ZIP_DEFLATED, ZipFile

from ..db import DEFAULT_DB
from ..db.atajos import get_backup_path, get_limite_backup_db
from .archivos import (borrar_archivo, lista_nombre_archivos, partir_ruta,
                       unir_ruta)


def hacer_backup_db() -> bool:
    """
    Realiza la compresión de una copia de la DB,
    y la almacena.

    Devuelve 'True' si todavía no se alcanzó el límite,
    sino elimina el más viejo y devuelve 'False'.
    """

    db_backup_path = f"{get_backup_path()}/db"
    lista_dir = lista_nombre_archivos(db_backup_path)
    res = True

    if len(lista_dir) >= get_limite_backup_db():
        borrar_archivo(unir_ruta(db_backup_path, min(lista_dir)))
        res = False

    nombre = f"db_{datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')}.zip"

    with ZipFile(file=unir_ruta(db_backup_path, nombre),
                 mode='w',
                 compression=ZIP_DEFLATED) as zf:
        zf.write(filename=DEFAULT_DB, arcname=partir_ruta(DEFAULT_DB)[1])

    return res