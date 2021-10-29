"""
Módulo hecho para trabajar con archivos, como leer y cargar
información persistente.
"""

from csv import reader

DiccionarioPares = dict[str, str]

def cargar_pares_valores(nombre_archivo: str) -> DiccionarioPares:
    """
    Lee el archivo de prefijos y devuelve un diccionario con
    cada server y su prefijo asignado mapeados en un diccionario.
    """

    dic_pares_valores = dict()

    with open(nombre_archivo, 'r') as archivo:

        prefijos = reader(archivo, delimiter='=')

        for clave, valor in prefijos:

            dic_pares_valores[clave] = valor

    return dic_pares_valores

def guardar_pares_valores(dic_pares_valores: DiccionarioPares, nombre_archivo: str) -> None:
    """
    Recibe un diccionario y guarda la información de este en un archivo CSV.
    """

    lista_a_imprimir = list()

    with open(nombre_archivo, 'w') as archivo:

        for clave, valor in dic_pares_valores.items():

            lista_a_imprimir.append(f"{clave}={valor}")

        archivo.write('\n'.join(lista_a_imprimir))
