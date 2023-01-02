"""
Módulo para atajos de sacar datos de una DB.
"""

from os import PathLike
from typing import TYPE_CHECKING, Tuple

from ..database import sacar_datos_de_tabla

if TYPE_CHECKING:
    from ..database import FetchResult


def get_propiedad(propiedad: str) -> "FetchResult":
    "Consigue alguna propiedad de BotShot."

    return sacar_datos_de_tabla("propiedades",
                                sacar_uno=True,
                                nombre=propiedad)[2]


def get_version() -> str:
    "Consigue la versión de BotShot."

    return get_propiedad("version")


def get_botshot_id() -> int:
    "Consigue el ID de BotShot."

    return int(get_propiedad("botshot_id"))


def get_prefijo_default() -> str:
    "Consigue el prefijo por defecto de BotShot."

    return get_propiedad("prefijo_default")


def get_limite_backup_db() -> int:
    "Consigue el limite de backups de DB asignados."

    return int(get_propiedad("limite_backup_db"))


def get_path_de_db(nombre_path: str) -> PathLike:
    "Consigue un path de la DB."

    res = sacar_datos_de_tabla("paths",
                               sacar_uno=True,
                               nombre_path=nombre_path)

    # El valor siempre será la tercera columna
    return res[2]


def get_paths_de_db(nombre_path: str) -> Tuple[PathLike, ...]:
    "Consigue muchos paths de la DB."

    res = sacar_datos_de_tabla("paths",
                               sacar_uno=False,
                               nombre_path=nombre_path)

    # Los valores siempre serán la tercera columna
    return tuple(col[2] for col in res)


def get_imagenes_path() -> PathLike:
    "Consigue el path de la carpeta 'images'."

    return get_path_de_db("imagenes")


def get_cogs_path() -> PathLike:
    "Consigue el path de los cogs."

    return get_path_de_db("cogs")


def get_log_path() -> PathLike:
    "Consigue el path del log."

    return get_path_de_db("log")


def get_backup_path() -> PathLike:
    "Consigue el path de los backups."

    return get_path_de_db("backup")


def get_sonidos_path() -> PathLike:
    "Consigue el path de los sonidos."

    return get_path_de_db("sonidos")


def get_prefijo_guild(guild_id: int) -> str:
    "Devuelve un prefijo por id del guild."

    res = sacar_datos_de_tabla("prefijos",
                               sacar_uno=True,
                               id_guild=guild_id)

    if not res:
        return get_prefijo_default()

    return res[2]


def get_canales_escuchados() -> dict[int, tuple[tuple[int, str], ...]]:
    """
    Devuelve un diccionario en el cual las claves son ids de guilds,
    y los valores una tupla en el que sus elementos son otras subtuplas.
    Estas subtuplas tienen el id y el nombre de los canales pertenecientes
    a ese guild.
    """

    datos = sacar_datos_de_tabla(tabla="canales_escuchables")
    dic_final = {}

    for id_canal, id_guild, nombre_canal in datos:
        if id_guild not in dic_final:
            dic_final[id_guild] = []
        
        dic_final[id_guild].append((id_canal, nombre_canal))


    # inmutar el dic
    for lista_ch in dic_final.values():
        for datos_ch in lista_ch:
            datos_ch = tuple(datos_ch)
        lista_ch = tuple(lista_ch)

    return dic_final


def get_recomendaciones_carpetas() -> list[tuple[str, str, int]]:
    """
    Devuelve los datos de las recomendaciones hechas por usuarios.
    """

    datos = []

    for dato in sacar_datos_de_tabla(tabla="carpetas_recomendadas",
                                     sacar_uno=False):
        datos.append(dato[1:])

    return datos


def get_usuarios_autorizados() -> list[Tuple[int, str, int]]:
    """
    Devuelve los datos de los usuarios autorizados.
    """

    return sacar_datos_de_tabla(tabla="usuarios_autorizados",
                                sacar_uno=False)
