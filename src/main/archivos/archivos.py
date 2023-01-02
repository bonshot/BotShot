"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from datetime import datetime
from os import PathLike, listdir, mkdir, path, remove, rmdir
from pathlib import Path
from random import choice
from typing import List, Optional, TypeAlias
from zipfile import ZIP_DEFLATED, ZipFile

from ..db import DEFAULT_DB
from ..db.atajos import get_backup_path, get_limite_backup_db

DiccionarioPares: TypeAlias = dict[str, str]


def unir_ruta(ruta: PathLike, sub_ruta: PathLike) -> str:
    """
    Une dos rutas con diferentes caracteres segun
    el sistema operativo.
    """

    return path.join(ruta, sub_ruta)


def partir_ruta(path_dir: PathLike) -> tuple[str, str]:
    """
    Parte una ruta en la 'cola' de la ruta, y el resto.
    """

    return path.split(path_dir)


def crear_dir(ruta: PathLike) -> None:
    """
    Crea un nuevo directorio en la ruta especificada.
    """

    mkdir(ruta)


def borrar_dir(ruta: PathLike) -> None:
    """
    Intenta borrar el directorio especificado.
    """

    rmdir(ruta)


def lista_nombre_carpetas(ruta: PathLike) -> list[PathLike]:
    """
    Devuelve una lista de los nombres de todas las carpetas
    que haya en la ruta indicada.
    """
    return [dir for dir in listdir(ruta) if path.isdir(unir_ruta(ruta, dir))]


def lista_nombre_archivos(ruta: PathLike, ext: Optional[str]=None) -> List[PathLike]:
    """
    Busca en la ruta especificada si hay archivos, y devuelve una lista
    con los nombres (no las rutas) de los que encuentre.

    Si `ext` no es `None`, entonces probará buscando archivos con esa extensión.
    `ext` NO debe tener un punto (`.`) adelante, es decir que `"py"` será automáticamente
    tratado como `.py`.
    """

    return [file for file in listdir(ruta) if ((path.isfile(unir_ruta(ruta, file)))
                                               and (file.endswith(f".{ext}") if ext else True))]


def buscar_rutas(patron: str="*",
                 nombre_ruta: Optional[PathLike]=None,
                 recursivo: bool=True,
                 incluye_archivos: bool=True,
                 incluye_carpetas: bool=True) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por los archivos
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    ruta = Path(nombre_ruta if nombre_ruta is not None else ".")

    return list(fpath.as_posix() for fpath in (ruta.rglob(patron) if recursivo else ruta.glob(patron))
                if (fpath.is_file() if incluye_archivos else False
                    or fpath.is_dir() if incluye_carpetas else False))


def buscar_archivos(patron: str="*",
                    nombre_ruta: Optional[PathLike]=None,
                    recursivo: bool=True) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por las rutas
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    return buscar_rutas(patron=patron,
                        nombre_ruta=nombre_ruta,
                        recursivo=recursivo,
                        incluye_archivos=True,
                        incluye_carpetas=False)


def buscar_carpetas(patron: str="*",
                    nombre_ruta: Optional[PathLike]=None,
                    recursivo: bool=True) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por las carpetas
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    return buscar_rutas(patron=patron,
                        nombre_ruta=nombre_ruta,
                        recursivo=recursivo,
                        incluye_archivos=False,
                        incluye_carpetas=True)


def carpeta_random(ruta: PathLike, incluir_subcarpetas: bool=True) -> Optional[PathLike]:
    """
    Devuelve la ruta a una carpeta aleatoria dentro de una ruta
    indicada.
    """
    opciones = buscar_carpetas(nombre_ruta=ruta, recursivo=incluir_subcarpetas)
    return choice(opciones) if opciones else None


def archivo_random(ruta: PathLike, incluir_subcarpetas: bool=True) -> Optional[PathLike]:
    """
    Devuelve un archivo aleatorio dentro de una ruta indicada. Si no hay
    nada en el directorio devuelve `None`.

    Si 'incluir_subcarpetas' es `True`, entonces busca recursivamente
    en los subdirectorios también.
    """

    opciones = buscar_archivos(nombre_ruta=ruta, recursivo=incluir_subcarpetas)
    return choice(opciones) if opciones else None


def tiene_subcarpetas(path_dir: PathLike) -> bool:
    """
    Verifica si una carpetas tiene carpetas hijas.
    """

    for elemento in Path(path_dir).iterdir():
        if elemento.is_dir():
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
    lista_dir = lista_nombre_archivos(db_backup_path)
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
