"""
Módulo para atajos de consulta a la db.
"""

from ..database import existe_dato_en_tabla


def existe_canal_escuchado(id_canal: int) -> bool:
    """
    Verifica si existe el canal entre los escuchados
    por BotShot.
    """

    return existe_dato_en_tabla(tabla="canales_escuchables",
                                id=id_canal)

