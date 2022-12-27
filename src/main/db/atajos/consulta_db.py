"""
Módulo para atajos de consulta a la db.
"""

from ..database import existe_dato_en_tabla
from .sacar_db import get_usuarios_autorizados


def existe_canal_escuchado(id_canal: int) -> bool:
    """
    Verifica si existe el canal entre los escuchados
    por BotShot.
    """

    return existe_dato_en_tabla(tabla="canales_escuchables",
                                id=id_canal)


def existe_usuario_autorizado(id_usuario: int) -> bool:
    """
    Verifica si existe el usuario autorizado con el id
    especificado.
    """

    for id_u, _, _ in get_usuarios_autorizados():
        if id_usuario == id_u:
            return True

    return False
