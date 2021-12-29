"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from json import load, dump

DiccionarioPares = dict[str, str]

def cargar_json(nombre_archivo: str) -> DiccionarioPares:
    """
    Lee y carga un archivo JSON.
    """
    dic_pares_valores = dict()

    with open(nombre_archivo, mode='r') as archivo:
        dic_pares_valores = load(archivo)
    return dic_pares_valores

def guardar_json(dic_pares_valores: DiccionarioPares, nombre_archivo: str) -> None:
    """
    Recibe un diccionario y guarda la informacion del mismo en un archivo JSON.
    """
    with open(nombre_archivo, mode='w') as archivo:
        dump(dic_pares_valores, archivo, indent=4)
