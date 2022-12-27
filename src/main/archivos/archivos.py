"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from datetime import datetime
from os import listdir, mkdir, path, remove, rmdir
from random import choice
from typing import List, Optional, TypeAlias
from zipfile import ZIP_DEFLATED, ZipFile

from ..db import DEFAULT_DB
from ..db.atajos import get_backup_path, get_limite_backup_db

DiccionarioPares: TypeAlias = dict[str, str]


def unir_ruta(ruta: str, sub_ruta: str) -> str:
    """
    Une dos rutas con diferentes caracteres segun
    el sistema operativo.
    """

    return path.join(ruta, sub_ruta)


def partir_ruta(path_dir: str) -> tuple[str, str]:
    """
    Parte una ruta en la 'cola' de la ruta, y el resto.
    """

    return path.split(path_dir)


def crear_dir(ruta: str) -> None:
    """
    Crea un nuevo directorio en la ruta especificada.
    """

    mkdir(ruta)


def borrar_dir(ruta: str) -> None:
    """
    Intenta borrar el directorio especificado.
    """

    rmdir(ruta)


def lista_carpetas(ruta: str) -> list[str]:
    """
    Devuelve una lista de todas las carpetas que haya en la ruta
    indicada.
    """
    return [dir for dir in listdir(ruta) if path.isdir(unir_ruta(ruta, dir))]


def lista_archivos(ruta: str, ext: Optional[str]=None) -> List[str]:
    """
    Busca en la ruta especificada si hay archivos, y devuelve una lista
    con los nombres de los que encuentre.

    Si `ext` no es `None`, entonces probará buscando archivos con esa extensión.
    `ext` NO debe tener un punto (`.`) adelante, es decir que `"py"` será automáticamente
    tratado como `.py`.
    """

    return [file for file in listdir(ruta) if ((not path.isdir(unir_ruta(ruta, file)))
                                               and (file.endswith(f".{ext}") if ext else True))]


def carpeta_random(ruta: str) -> str:
    """
    Devuelve la ruta a una carpeta aleatoria dentro de una ruta
    indicada.
    """
    return unir_ruta(ruta, choice(lista_carpetas(ruta)))


def archivo_random(ruta: str) -> str:
    """
    Devuelve un archivo aleatorio dentro de una ruta indicada.
    """
    return unir_ruta(ruta, choice(lista_archivos(ruta)))


def tiene_subcarpetas(path_dir: str) -> bool:
    """
    Verifica si una carpetas tiene carpetas hijas.
    """

    for elemento in listdir(path_dir):
        if path.isdir(unir_ruta(path_dir, elemento)):
            return True

    return False


def hacer_backup_db() -> bool:
    """
    Realiza la compresión de una copia de la DB,
    y la almacena.

    Devuelve 'True' si todavía no se alcanzó el límite,
    sino elimina el más viejo y devuelve 'False'.
    """

    db_backup_path = f"{get_backup_path()}/db"
    lista_dir = lista_archivos(db_backup_path)
    res = True

    if len(lista_dir) >= get_limite_backup_db():
        remove(unir_ruta(db_backup_path, min(lista_dir)))
        res = False

    nombre = f"db_{datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')}.zip"

    with ZipFile(file=unir_ruta(db_backup_path, nombre),
                 mode='w',
                 compression=ZIP_DEFLATED) as zf:
        zf.write(filename=DEFAULT_DB, arcname=partir_ruta(DEFAULT_DB)[1])

    return res
