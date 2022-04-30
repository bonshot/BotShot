"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from json import load, dump
from random import choice
from os import listdir, path, mkdir, rmdir
from typing import List, Optional

DiccionarioPares = dict[str, str]


def cargar_json(nombre_archivo: str) -> DiccionarioPares:
    """
    Lee y carga un archivo JSON.
    """
    dic_pares_valores = dict()

    with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
        dic_pares_valores = load(archivo)
    return dic_pares_valores


def guardar_json(dic_pares_valores: DiccionarioPares, nombre_archivo: str) -> None:
    """
    Recibe un diccionario y guarda la informacion del mismo en un archivo JSON.
    """
    with open(nombre_archivo, mode='w', encoding='utf-8') as archivo:
        dump(dic_pares_valores, archivo, indent=4)


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


def lista_archivos(ruta: str) -> list[str]:
    """
    Devuelve una lista de todos los nombres de archivos dentro
    de una ruta indicada.
    """
    return [file for file in listdir(ruta) if not path.isdir(unir_ruta(ruta, file))]


def get_nombre_archivos(ruta: str, ext: Optional[str]=None) -> List[str]:
    """
    Busca en la ruta especificada si hay archivos, y devuelve una lista
    con los nombres de los que encuentre.

    Si `ext` no es `None`, entonces probará buscando archivos con esa extensión.
    `ext` NO debe tener un punto (`.`) adelante, es decir que `"py"` será automáticamente
    tratado como `.py`.
    """

    return [file for file in listdir(ruta) if (file.endswith(f".{ext}") if ext else True)]


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
