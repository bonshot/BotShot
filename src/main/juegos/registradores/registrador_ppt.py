"""
Módulo para un registrador de Piedra, Papel o Tijeras.
"""

from typing import TYPE_CHECKING, Any

from ...db import CursorDesc, actualizar_dato_de_tabla, insertar_datos_en_tabla
from .registrador_abc import RegistradorBase, TiposColumnaDB, TiposDB

if TYPE_CHECKING:
    from discord import Embed

    from ..jugador import ListaJugadores


class RegistradorPPT(RegistradorBase):
    """
    Registrador de Piedra, Papel o Tijeras.
    """

    @staticmethod
    def nombre_tabla() -> str:
        """
        Devuelve el nombre de la tabla
        asociada a este registrador.
        """

        return "stats_ppt"


    @staticmethod
    def tipos_columnas() -> TiposColumnaDB:
        """
        Devuelve un diccionario que denota cuántas
        columnas de la tabla y de qué tipo deberían ser.
        """

        return {
            # "id_jugador: TiposDB.TEXT, esta es agregada automáticamente
            "victorias": TiposDB.INTEGER,
            "empates": TiposDB.INTEGER,
            "derrotas": TiposDB.INTEGER
        }


    def insertar_en_tabla(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Inserta en la tabla asociada.
        """

        vic = kwargs.get("victorias")
        emp = kwargs.get("empates")
        der = kwargs.get("derrotas")

        insertar_datos_en_tabla(tabla=self.nombre_tabla(),
                                llave_primaria_por_defecto=False,
                                valores=(id_jugador, vic, emp, der))


    def actualizar_tabla(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Actualiza la tabla asociada.
        """

        kwargs_red = {
            "victorias": kwargs.get("victorias"),
            "empates": kwargs.get("empates"),
            "derrotas": kwargs.get("derrotas")
        }

        for col, val in kwargs_red.items():
            actualizar_dato_de_tabla(tabla=self.nombre_tabla(),
                                     nombre_col=col,
                                     valor=val,
                                     id_jugador=id_jugador)


    def agregar_datos_a_embed(self,
                              embed: "Embed",
                              jugadores: "ListaJugadores",
                              en_linea: bool=True) -> "Embed":
        """
        Agrega su propio campo al embed del lobby.
        """

        stats = []
        for jug in jugadores:
            _, vic, emp, der = self.get_datos(jug.id, self.stats_base())
            stats.append(f"{vic} - {emp} - {der}")
        
        stats_str = "\n".join(stats)
        return embed.add_field(name="V - E - D", value=f"\n{stats_str}", inline=en_linea)


    @staticmethod
    def stats_base() -> Any:
        """
        Define la información inicial a encontrar si es la primera
        vez que se registra a un jugador.
        """

        return ("-id_basura-", 0, 0, 0)
