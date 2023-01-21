"""
Módulo para un registrador genérico de un juego.
"""

from abc import ABC, abstractmethod
from os import PathLike
from typing import Any, Optional, TypeAlias, TYPE_CHECKING

from ...db import (DEFAULT_DB, CursorDesc, DictLlaveForanea, FetchResult,
                   TiposDB, crear_tabla, existe_dato_en_tabla, existe_tabla,
                   sacar_datos_de_tabla)

if TYPE_CHECKING:
    from ..jugador import ListaJugadores
    from discord import Embed


ListaRegistradores: TypeAlias = list[type["RegistradorBase"]]
TiposColumnaDB: TypeAlias = dict[str, TiposDB]


class RegistradorBase(ABC):
    """
    Registrador genérico de un juego.

    Un registrador interactúa con la DB para
    archivar estadísticas, crear tablas de ser necesario,
    entre quizás otros eventos.
    """

    _ignorar: bool = False

    lista_registradores: ListaRegistradores = []


    def __init_subclass__(cls: type["RegistradorBase"]) -> None:
        """
        Registra un registrador. (Valga la redundancia)
        """

        if hasattr(cls, "_ignorar") and cls._ignorar is True:
            return

        __class__.lista_registradores.append(cls)


    def __init__(self, db_path: PathLike=DEFAULT_DB) -> None:
        """
        Inicializa un registrador.
        """

        self.db_path: PathLike = db_path


    @staticmethod
    @abstractmethod
    def nombre_tabla() -> str:
        """
        Devuelve el nombre de la tabla
        asociada a este registrador.
        """

        raise NotImplementedError


    @staticmethod
    @abstractmethod
    def tipos_columnas() -> TiposColumnaDB:
        """
        Devuelve un diccionario que denota cuántas
        columnas de la tabla y de qué tipo deberían ser.

        De todas formas se agrega una que siempre está:
        'id_jugador'.
        """

        raise NotImplementedError


    @staticmethod
    def llave_primaria() -> Optional[str]:
        """
        Método opcional, define si usar una llave
        primaria personalizada.

        Tiene que ser igual al nombre de una
        de las columnas para ser usado.

        Por defecto se va a utilizar 'id_jugador'.
        """

        return None


    @staticmethod
    def llaves_foraneas() -> DictLlaveForanea:
        """
        Método opcional para definir llaves foráneas
        a columnas de otras tablas.

        Tanto el nombre de la columna como el de la
        tabla foránea y columna foráneas deben ser
        todos existentes.
        """

        return None


    def crear_tabla(self) -> CursorDesc:
        """
        De ser necesario, crea la tabla que este
        registrador va a usar.

        Se da por hecho que la tabla no se ha creado
        todavía.
        """

        tipos_cols = ({"id_jugador": TiposDB.TEXT})
        tipos_cols.update(self.tipos_columnas())

        return crear_tabla(nombre=self.nombre_tabla(),
                           db_path=self.db_path,
                           estricta=True,
                           llave_primaria=(self.llave_primaria()
                                           if self.llave_primaria() is not None
                                           else "id_jugador"),
                           llaves_foraneas=(self.llaves_foraneas()
                                            if self.llaves_foraneas() is not None
                                            else {"id_jugador": ("jugador", "id")}),
                           **tipos_cols)


    def existe_jugador_en_tabla(self, id_jugador: str) -> bool:
        """
        Verifica si un jugador ya fue registrado en su respectiva tabla.
        """

        return existe_dato_en_tabla(self.nombre_tabla(), id_jugador=id_jugador)
    

    @abstractmethod
    def insertar_en_tabla(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Inserta en a la tabla asociada.
        """

        raise NotImplementedError


    @abstractmethod
    def actualizar_tabla(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Actualiza la tabla asociada.
        """

        raise NotImplementedError


    def refrescar_tabla(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Refresca la tabla asociada a este registrador.
        """

        if not self.existe_jugador_en_tabla(id_jugador):
            return self.insertar_en_tabla(id_jugador=id_jugador, **kwargs)

        return self.actualizar_tabla(id_jugador=id_jugador, **kwargs)


    def refrescar_datos(self, *, id_jugador: str, **kwargs) -> CursorDesc:
        """
        Refresca los datos de la tabla asociada a este registrador.
        """

        if not existe_tabla(self.nombre_tabla()):
            self.crear_tabla()

        return self.refrescar_tabla(id_jugador=id_jugador, **kwargs)


    def get_datos(self, id_jugador: str, default: Any) -> FetchResult:
        """
        Consigue los datos de un jugador.
        """

        res = sacar_datos_de_tabla(tabla=self.nombre_tabla(),
                                   sacar_uno=True,
                                   # Si ocurre algo, devolver None igualmente
                                   ignorar_excepciones=True,
                                   id_jugador=id_jugador)

        return (res if res is not None else default)


    @abstractmethod
    def agregar_datos_a_embed(self,
                              embed: "Embed",
                              jugadores: "ListaJugadores",
                              en_linea: bool=True) -> "Embed":
        """
        Agrega su propio campo al embed del lobby.
        """

        raise NotImplementedError


    @staticmethod
    @abstractmethod
    def stats_base() -> Any:
        """
        Define la información inicial a encontrar si es la primera
        vez que se registra a un jugador.
        """

        raise NotImplementedError
