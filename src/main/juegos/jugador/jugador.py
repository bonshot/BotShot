"""
Módulo para el modelado de un jugador.
"""

from typing import Optional, TypeAlias
from io import BytesIO

from discord import User

from ...db.atajos import get_jugador, registrar_jugador

LONGITUD_MAXIMA_NOMBRE = 30
"""
Longitud máxima que debe tener un nombre de jugador.
"""

ListaJugadores: TypeAlias = list["Jugador"]


class Jugador:
    """
    Clase que emula un jugador.
    """

    @classmethod
    def desde_usuario_discord(cls, usuario: User) -> "Jugador":
        """
        Trata de cargar un usuario de discord guardado en la
        DB como un jugador, sino crea uno nuevo.
        """

        jug = get_jugador(str(usuario.id))
        extras = {
            "discriminador": usuario.discriminator
        }

        if jug is None:
            registrar_jugador(id_jugador=str(usuario.id),
                              nombre=usuario.display_name)
            return cls(nombre=usuario.display_name,
                       id=str(usuario.id),
                       **extras)

        id_jug, nombre, emoji, img = jug
        return cls(nombre=nombre,
                   id=id_jug,
                   emoji_preferido=emoji,
                   foto_perfil=img,
                   **extras)


    def __init__(self,
                 nombre: str,
                 id: str,
                 emoji_preferido: Optional[str]=None,
                 foto_perfil: Optional[BytesIO]=None,
                 **kwargs) -> None:
        """
        Inicializa una instancia de 'Jugador'.

        'nombre' e 'id' son obligatorios, pues son lo que se usa para identificar al jugador.

        Los argumentos extra se guardan en un atributo especial 'extras'
        """

        self.nombre: str = (nombre
                            if len(nombre) <= LONGITUD_MAXIMA_NOMBRE
                            else nombre[:LONGITUD_MAXIMA_NOMBRE])
        self.id: str = id
        self.emoji: Optional[str] = emoji_preferido
        self.foto_perfil: Optional[BytesIO] = foto_perfil
        self.prof_seek(0) # Por si las moscas, devolver la posición al principio

        self.extras: dict = kwargs


    def __eq__(self, otro: "Jugador") -> bool:
        """
        Determina si dos jugadores son iguales.
        """

        return self.id == otro.id and self.nombre == otro.nombre


    def cambiar_nombre(self, nuevo_nombre: str) -> bool:
        """
        Intenta cambiar el nombre del jugador.

        Si tiene éxito, devuelve `True`, o sino devuelve `False`.
        """

        if (not isinstance(nuevo_nombre, str)
            or len(nuevo_nombre) > LONGITUD_MAXIMA_NOMBRE):
            return False

        self.nombre = nuevo_nombre
        return True


    def prof_seek(self, offset: int, whence: int=0, /) -> None:
        """
        Devuelve el puntero del búfer a la posición indicada.
        """

        if self.foto_perfil is not None:
            self.foto_perfil.seek(offset, whence)
