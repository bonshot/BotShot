"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from os import PathLike
from pathlib import Path
from random import choice
from re import match
from typing import List, Optional, TypeAlias

DiccionarioPares: TypeAlias = dict[str, str]


def unir_ruta(ruta: PathLike, sub_ruta: PathLike) -> str:
    """
    Une dos rutas con diferentes caracteres segun
    el sistema operativo.
    """

    return Path(ruta) / sub_ruta


def partir_ruta(ruta: PathLike) -> tuple[str, str]:
    """
    Parte una ruta en la 'cola' de la ruta, y el resto.
    """

    path = Path(ruta)
    return path.parent, path.name


def existe(ruta: PathLike) -> bool:
    """
    Verifica si una ruta ya está creada.
    """

    return Path(ruta).exists()


def crear_dir(ruta: PathLike, crear_dir_padres: bool=True) -> None:
    """
    Crea un nuevo directorio en la ruta especificada.
    """

    Path(ruta).mkdir(parents=crear_dir_padres)


def borrar_dir(ruta: PathLike) -> None:
    """
    Intenta borrar el directorio especificado.
    """

    Path(ruta).rmdir()


def borrar_archivo(ruta: PathLike, ignorar_excepciones: bool=False) -> None:
    """
    Borra un archivo en la ruta especificada.
    """

    Path(ruta).unlink(missing_ok=ignorar_excepciones)


def repite_nombre(ruta: PathLike, ignorar_ext: bool=False) -> PathLike:
    """
    Busca por nombres repetidos y con similar patrón en el directorio.
    Devuelve la misma ruta o una modificada de ser necesario.

    Si 'ignorar_ext' es `True`, entonces se ignora archivos de igual
    nombre pero distinta extensión.
    """

    ruta_final = Path(ruta)

    repetidos = 0

    dir_padre = ruta_final.parent
    if not dir_padre.exists():
        dir_padre.mkdir()

    nombre = ruta_final.stem
    ext = ruta_final.suffix

    lleva_ext = rf"\{ext}$" if not ignorar_ext else r"\.(\w)+$"
    patron = rf"^{nombre}(_(\d)+)?{lleva_ext}"

    for hijo in dir_padre.iterdir():
        if match(patron, hijo.name):
            repetidos += 1

    if repetidos > 0:
        ruta_final = ruta_final.with_stem(f"{nombre}_{repetidos}")

    if ruta_final.exists():
        return repite_nombre(ruta_final, ignorar_ext=ignorar_ext)

    return ruta_final.as_posix()


def lista_nombre_carpetas(ruta: PathLike) -> list[PathLike]:
    """
    Devuelve una lista de los nombres de todas las carpetas
    que haya en la ruta indicada.
    """

    path = Path(ruta)
    dirs = []

    for p in path.iterdir():
        if p.is_dir():
            dirs.append(p.name)

    return dirs


def lista_nombre_archivos(ruta: PathLike,
                          ext: Optional[str]=None,
                          ignorar_nombres: tuple[str, ...]=()) -> List[PathLike]:
    """
    Busca en la ruta especificada si hay archivos, y devuelve una lista
    con los nombres (no las rutas) de los que encuentre.

    Si `ext` no es `None`, entonces probará buscando archivos con esa extensión.
    `ext` NO debe tener un punto (`.`) adelante, es decir que `"py"` será automáticamente
    tratado como `.py`.
    """

    path = Path(ruta)
    archs = []

    for p in path.iterdir():
        if (p.is_file()
            and ((p.suffix == f".{ext}") if ext else True)
            and all(p.stem != nombre for nombre in ignorar_nombres)):
            archs.append(p.name)

    return archs


def buscar_rutas(patron: str="*",
                 nombre_ruta: Optional[PathLike]=None,
                 recursivo: bool=True,
                 incluye_archivos: bool=True,
                 incluye_carpetas: bool=True,
                 ignorar_patrones: tuple[str, ...]=()) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por los archivos
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    ruta = Path(nombre_ruta if nombre_ruta is not None else ".")

    return list(fpath.as_posix() for fpath in (ruta.rglob(patron)
                                               if recursivo
                                               else ruta.glob(patron))
                if ((fpath.is_file() if incluye_archivos else False
                    or fpath.is_dir() if incluye_carpetas else False)
                    and all(not fpath.match(patr) for patr in ignorar_patrones)))


def buscar_archivos(patron: str="*",
                    nombre_ruta: Optional[PathLike]=None,
                    recursivo: bool=True,
                    ignorar_patrones: tuple[str, ...]=()) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por las rutas
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    return buscar_rutas(patron=patron,
                        nombre_ruta=nombre_ruta,
                        recursivo=recursivo,
                        incluye_archivos=True,
                        incluye_carpetas=False,
                        ignorar_patrones=ignorar_patrones)


def buscar_carpetas(patron: str="*",
                    nombre_ruta: Optional[PathLike]=None,
                    recursivo: bool=True,
                    ignorar_patrones: tuple[str, ...]=()) -> list[PathLike]:
    """
    Busca recursivamente en todas las subrutas por las carpetas
    que coincidan con el patrón dado.
    Si `ruta` no está definida se usa el directorio actual.
    """

    return buscar_rutas(patron=patron,
                        nombre_ruta=nombre_ruta,
                        recursivo=recursivo,
                        incluye_archivos=False,
                        incluye_carpetas=True,
                        ignorar_patrones=ignorar_patrones)


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

