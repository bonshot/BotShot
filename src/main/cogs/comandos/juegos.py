"""
Cog para manejar comandos de juegos.
"""

from io import BytesIO
from random import randint
from typing import TYPE_CHECKING, Optional

from discord import Attachment, Colour, Embed, File, Interaction
from discord.app_commands import Choice, autocomplete, choices
from discord.app_commands import command as appcommand
from discord.app_commands import describe
from emoji import is_emoji
from PIL.Image import open as img_open

from ...auxiliares import (autocompletado_nombres_jugadores,
                           autocompletado_nombres_manejadores)
from ...db.atajos import (actualizar_emoji_de_jugador,
                          actualizar_foto_perfil_de_jugador,
                          actualizar_nombre_de_jugador,
                          existe_jugador_registrado, get_jugador,
                          registrar_jugador)
from ...interfaces import SelectorJuegos
from ...juegos import LONGITUD_MAXIMA_NOMBRE
from ...juegos.manejadores import ManejadorBase
from ..cog_abc import GroupsList, _CogABC, _GrupoABC

if TYPE_CHECKING:

    from ...botshot import BotShot

MIN_W: int = 250
MIN_H: int = 250


class GrupoJugador(_GrupoABC):
    """
    Grupo para comandos que interactúan con objetos 'Jugador'.
    """

    def __init__(self, bot: "BotShot") -> None:
        """
        Inicializa una instacia de 'GrupoJugador'.
        """

        super().__init__(bot,
                         name="jugador",
                         description="Comandos para interactuar con jugadores.")


    def _es_convertible(self, emoji: str) -> bool:
        """
        Define si un string es convertible al formato 'U+XXXX'.
        """

        try:
            f"{ord(emoji):X}"
        except:
            return False
        else:
            return True


    def _color_aleatorio(self) -> str:
        """
        Devuelve un color aleatorio en forma de string.
        """

        num =  f"{randint(0x000000, 0xFFFFFF):X}".zfill(6)
        return f"#{num}"


    def _verificar_jugador(self, id_jugador: str, nombre_jugador: str) -> bool:
        """
        Verifica si existe un jugador. Si no, lo crea.
        """

        if existe_jugador_registrado(id_jugador):
            return True

        registrar_jugador(id_jugador=id_jugador,
                          nombre=nombre_jugador)
        return False


    @appcommand(name="nombre",
                description="Cambiar el nombre del jugador asociado.")
    @describe(nuevo_nombre="El nuevo nombre a utilizar.")
    async def cambiar_nombre(self, interaccion: Interaction, nuevo_nombre: str) -> None:
        """
        Cambia el nombre de un jugador.
        """

        if len(nuevo_nombre) > LONGITUD_MAXIMA_NOMBRE:
            msg = (f"**Nombre `{nuevo_nombre}` no permitido.** Debe tener como máximo " +
                   f"{LONGITUD_MAXIMA_NOMBRE} caracteres.")
            await interaccion.response.send_message(content=msg,
                                                    ephemeral=True)
            return

        autor = interaccion.user
        id_jug = str(autor.id)
        nombre_jug = autor.display_name

        self._verificar_jugador(id_jug, nombre_jug)

        actualizar_nombre_de_jugador(id_jugador=id_jug,
                                     nuevo_nombre=nuevo_nombre)
        msg = f"*Nombre cambiado a* `{nuevo_nombre}` *correctamente.*"
        await interaccion.response.send_message(content=msg,
                                                ephemeral=True)


    @appcommand(name="emoji",
                description="Cambiar el emoji del jugador asociado.")
    @describe(nuevo_emoji="El nuevo emoji a utilizar.")
    async def cambiar_emoji(self, interaccion: Interaction, nuevo_emoji: str) -> None:
        """
        Cambia el emoji de un jugador.
        """

        if not self._es_convertible(nuevo_emoji):
            msg = "*Yo no puedo usar ese emoji.*"

        elif not is_emoji(nuevo_emoji):
            msg = "*Emoji no válido.*"

        else:
            msg = f"*Emoji cambiado a* `{nuevo_emoji}` *correctamente.*"
            codepoint = f"U+{ord(nuevo_emoji):X}" # U+XXXX

            autor = interaccion.user
            id_jug = str(autor.id)
            nombre_jug = autor.display_name

            self._verificar_jugador(id_jug, nombre_jug)
            actualizar_emoji_de_jugador(id_jug, codepoint)

        await interaccion.response.send_message(content=msg,
                                                ephemeral=True)


    async def _procesar_imagen(self, imagen: Attachment) -> BytesIO:
        """
        Procesa la imagen para que sea cuadrada y de formato PNG.
        """

        img_obj = BytesIO()
        final_img = BytesIO()
        await imagen.save(img_obj, seek_begin=True)

        with img_open(img_obj) as im:
            if im.width > im.height:
                im = im.resize((im.height, im.height))
            
            elif im.height > im.width:
                im = im.resize((im.width, im.width))

            im.convert("RGBA").save(final_img, format="PNG")

        final_img.seek(0) # por si las moscas
        return final_img


    @appcommand(name="imagen",
                description="Cambiar la foto de perfil del jugador asociado.")
    @describe(nueva_imagen="La nueva imagen a utilizar.")
    async def cambiar_foto_perfil(self, interaccion: Interaction, nueva_imagen: Attachment) -> None:
        """
        Cambia la imagen de perfil de un jugador.
        """

        if "image" not in nueva_imagen.content_type:
            msg = "*Este archivo no es una imagen. Sube una preferentemente de formato `PNG`.*"
        
        elif (nueva_imagen.width < MIN_W or nueva_imagen.height < MIN_H):
            w, h = nueva_imagen.width, nueva_imagen.height
            msg = (f"Tamaño de imagen **{w}x{h} px** no válida. Debe de ser como mínimo de " +
                   f"**{MIN_W}x{MIN_H} px**.")

        else:
            msg = f"Imagen `{nueva_imagen.filename}` actualizada correctamente."
            autor = interaccion.user
            id_jug = str(autor.id)
            nombre_jug = autor.display_name

            self._verificar_jugador(id_jug, nombre_jug)
            actualizar_foto_perfil_de_jugador(id_jug,
                                              await self._procesar_imagen(nueva_imagen))

        await interaccion.response.send_message(content=msg,
                                                ephemeral=True)


    @appcommand(name="perfil",
                description="Muestra una presentación básica de un jugador.")
    @describe(jugador="El jugador a mostrar.",
              efimero="Si el resultado se debería mostrar sólo a ti.")
    @choices(efimero=[
        Choice(name="Sí", value=1),
        Choice(name="No", value=0)
    ])
    @autocomplete(jugador=autocompletado_nombres_jugadores)
    async def mostrar_perfil_jugador(self,
                                     interaccion: Interaction,
                                     jugador: Optional[str]=None,
                                     efimero: Choice[int]=1) -> None:
        """
        Muestra información básica de un jugador.
        """

        es_efimero = bool((efimero.value if isinstance(efimero, Choice) else efimero))
        await interaccion.response.defer(ephemeral=es_efimero)

        autor = interaccion.user
        id_autor = str(autor.id)
        nombre_autor = autor.display_name
        self._verificar_jugador(id_autor, nombre_autor)

        info_jug = (get_jugador(id_autor) if jugador is None else get_jugador(jugador))
        id_jug, nombre_jug, emoji_jug, img_jug = info_jug
        usuario = await self.bot.fetch_user(int(id_jug))
        img_autor = await self.bot.fetch_avatar(int(id_jug))

        if img_jug is not None:
            with img_open(img_jug) as im:
                fmt = im.format
                img_w, img_h = im.size
            img_jug.seek(0) # Al leerlo hace falta devolverlo a 0

        miniatura = (img_jug if img_jug is not None else img_autor)
        emoji_val = (emoji_jug if emoji_jug is not None else "*Ninguno*")
        img_val = (f"*{fmt.upper()} de tamaño {img_w}x{img_h} px*"
                   if img_jug is not None
                   else "*Ninguna*")
        embed = Embed(title=f"Info. de {nombre_jug}",
                      color=Colour.from_str(self._color_aleatorio()))

        miniatura_arch = File(miniatura, filename="miniatura.png")
        embed.set_thumbnail(url="attachment://miniatura.png")\
             .set_author(name=usuario.display_name, icon_url=usuario.display_avatar.url)\
             .add_field(name="Nombre", value=nombre_jug, inline=True)\
             .add_field(name="id", value=id_jug, inline=True)\
             .add_field(name="Emoji", value=emoji_val, inline=True)\
             .add_field(name="Imagen", value=img_val, inline=True)

        mens = await interaccion.followup.send(wait=True, # Para que devuelva el mensaje
                                               file=miniatura_arch, # necesario para el embed
                                               embed=embed,
                                               ephemeral=es_efimero)

        if not es_efimero:
            await mens.delete(delay=15.0)


class CogJuegos(_CogABC):
    """
    Cog para comandos de manejar juegos.
    """

    @classmethod
    def grupos(cls) -> GroupsList:
        """
        Devuelve la lista de grupos asociados a este Cog.
        """

        return [GrupoJugador]


    @appcommand(name="jugar",
                description="Inicia una partida de algún juego.")
    @describe(juego="El juega a iniciar.")
    @autocomplete(juego=autocompletado_nombres_manejadores)
    async def init_diversion(self, interaccion: Interaction, juego: Optional[str]) -> None:
        """
        Inicia algún juego.
        """

        if juego is None:
            await interaccion.response.send_message(content="Por favor elige un juego:",
                                                    ephemeral=True,
                                                    view=SelectorJuegos(self.bot))
            return

        for manejador in ManejadorBase.lista_clases_manejadores:
            if juego == manejador.nombre_juego():
                await SelectorJuegos.iniciar_lobby(clase_manejador=manejador,
                                                   interaccion=interaccion,
                                                   bot=self.bot,
                                                   editar=False)
                break


async def setup(bot: "BotShot"):
    """
    Agrega el cog de este módulo a BotShot.
    """

    await bot.add_cog(CogJuegos(bot))
