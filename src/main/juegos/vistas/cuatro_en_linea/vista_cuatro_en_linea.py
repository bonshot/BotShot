"""
Módulo para la vista de una partida de 4 en Línea.
"""

from io import BytesIO
from typing import TYPE_CHECKING, Any, Optional

from discord import File, Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle
from discord.ui import Button
from PIL.Image import new as img_new
from PIL.Image import open as img_open
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

from ....db.atajos import get_img_juegos_path, get_minecraftia_font
from ..vista_juego_abc import VistaJuegoBase
from ..vista_reiniciar_abc import VistaReiniciarBase

if TYPE_CHECKING:
    from discord import Message
    from PIL.Image import Image

    from ....botshot import BotShot
    from ...modelos import JuegoBase
    from ...registradores import RegistradorBase


class VistaReiniciarCuatroEnLinea(VistaReiniciarBase):
    """
    Vista para reiniciar el 4 en Línea.
    """

    async def reiniciar_extra(self, _interaccion: Interaction) -> None:
        """
        Reinicia el 4 en Línea.
        """

        self.maestra.modelo.opciones.cambiar_orden_jugadores()


class BotonColumna(Button):
    """
    Botón para mover en una columna.
    """

    def __init__(self, vista_maestra: "VistaCuatroEnLinea", col: int) -> None:
        """
        Inicializa un botón de columna.
        """

        super().__init__(style=ButtonStyle.gray,
                         label=f"{col + 1}",
                         disabled=False,
                         custom_id=f"connect_four_col_{col}",
                         # A papa discord no le gustan más de 5 botones en una sola fila
                         row=(0 if col < 4 else 1))

        self.maestra: "VistaCuatroEnLinea" = vista_maestra
        self.col: int = col


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Un jugador apretó un botón de columna.
        """

        await self.maestra.seguir(interaccion, self)


class VistaCuatroEnLinea(VistaJuegoBase):
    """
    Vista de una partida de 4 en Línea.
    """

    def __init__(self,
                 bot: "BotShot",
                 modelo: "JuegoBase",
                 registrador: Optional["RegistradorBase"],
                 mensaje_raiz: Optional["Message"]) -> None:
        """
        Inicializa una instancia de una vista de juego.
        """

        super().__init__(bot=bot,
                         modelo=modelo,
                         registrador=registrador,
                         mensaje_raiz=mensaje_raiz)

        for i in range(7):
            self.add_item(BotonColumna(vista_maestra=self,
                                       col=i))

        # Propiedades de la imagen del tablero
        self.diam: int = 70
        "Diámetro de los círculos de las casillas."
        self.dix: int = 15
        "Diferencia horizontal en los bordes."
        self.diy: int = 5
        "Diferencia vertical en los bordes."
        self.dx: int = 20
        "Diferencia horizontal."
        self.dy: int = 10
        "Diferencia vertical."

        with img_open(f"{get_img_juegos_path()}/4_en_linea/4_en_linea_tablero.png",
                      formats=("png",)) as im:
            self.img: "Image" = self._generar_img(im)


    @staticmethod
    def get_cerrar_id() -> str:
        """
        El ID del botón para cerrar la vista.
        """

        return "connect_four_close"


    def _generar_img(self, im: "Image") -> "Image":
        """
        Genera una imagen con las condiciones ideales para ser editada.
        """

        w, h = im.size
        img = img_new(mode="RGBA", size=(w, h + self.diy + (3 * self.dy)))
        img.paste(im.copy())
        dr = Draw(img)

        dr.rectangle((0, h + self.diy, w, h + self.diy + (3 * self.dy)),
                     fill="#3c7de6")

        for i in range(self.modelo.dim_x):

            tx = self.dix + i * (self.dx + self.diam) + (self.diam // 2)
            dr.text((tx, h + self.diy + (1.5 * self.dy)), f"{i + 1}",
                    font=truetype(get_minecraftia_font(), 18),
                    fill="#ffffff",
                    anchor="mm")
            
            lx = (self.dix if i > 0 else 0) + i * (self.dx + self.diam) - (self.dx // 2)
            dr.line((lx, h + self.diy, lx, h + self.diy + (3 * self.dy)),
                    fill="#2e6ac9", width=4)

        return img


    async def setup(self) -> None:
        """
        Da inicio al juego.
        """

        await self.mensaje_raiz.delete()
        mens = await self.mensaje_raiz.channel.send(content=self.modelo.mensaje,
                                                    file=self.arch_img(),
                                                    view=self)
        self.mensaje_raiz = mens


    def es_jugador_actual(self, id_jugador: str) -> bool:
        """
        Determina si es el jugador actual.
        """

        return id_jugador == self.modelo.jugador_actual.id


    def refrescar_imagen(self, img_x: int, img_y: int) -> None:
        """
        Dibuja la ficha recién puesta en la imagen del tablero.
        """

        x1 = self.dix + img_x * (self.dx + self.diam)
        y1 = self.diy + img_y * (self.dy + self.diam)

        dr = Draw(self.img)
        dr.ellipse((x1,
                    y1,
                    x1 + self.diam, # x2
                    y1 + self.diam, # y2
                   ),
                   fill=(self.modelo.color_actual
                         if self.modelo.terminado()
                         else self.modelo.color_anterior),
                   outline="#3c7ae6",
                   width=2)


    async def seguir(self, interaccion: Interaction, boton: BotonColumna) -> None:
        """
        Prosigue con el 4 en Línea.
        """

        autor = interaccion.user

        if not self.es_jugador_actual(str(autor.id)):
            msg = (self.modelo.mensaje + 
                   f"\n\nPero, {autor.mention}, o vos no estás jugando o a vos no te toca.")
            await self.refrescar_mensaje(interaccion, msg)
            return

        self.modelo.actualizar(col=boton.col)

        if self.modelo.col_esta_llena(boton.col):
            boton.disabled = True

        if not self.modelo.opciones.modo_texto:
            img_x, img_y = self.modelo.ultima_ficha
            self.refrescar_imagen(img_x, img_y)
        await self.refrescar_mensaje(interaccion)


    def guardar_img(self) -> BytesIO:
        """
        Guarda la imagen en un archivo en memoria.
        """

        arch = BytesIO()
        self.img.save(arch, "PNG")
        arch.seek(0) # La operación de arriba deja el puntero al final del búfer

        return arch


    def arch_img(self) -> File:
        """
        Crea un archivo listo para mandarse en mensajes.
        """

        return File(fp=self.guardar_img(), filename="4_en_línea.png")


    async def refrescar_mensaje(self,
                                 interaccion: Interaction,
                                 mensaje: Optional[str]=None):
        """
        Actualiza el mensaje de la partida.
        """

        # borramos el mensaje actual, lo cambiamos por otro
        await interaccion.response.edit_message(content="*Cargando...*",
                                                view=None)
        await self.mensaje_raiz.delete()

        arch = (self.arch_img()
                if not self.modelo.opciones.modo_texto
                else None)

        if not self.modelo.terminado():

            msg = (self.modelo.mensaje if mensaje is None else mensaje)
            mens = await interaccion.channel.send(content=msg,
                                                  file=arch,
                                                  view=self)

        else:
            msg = ((f"Ganó **{self.modelo.jugador_actual.nombre}" +
                    (f" ({self.modelo.letra_actual})**"
                    if self.modelo.opciones.modo_texto
                    else "**"))
                    if not self.modelo.empate()
                    else "Es un empate.")

            self.refrescar_stats_cuatro_en_linea()
            self.clear_items()
            jug = self.modelo.cantidad_jugadores
            mens = await interaccion.channel.send(content=(msg + f"\n\n¿Otra partida? " +
                                                                 f"**(0 / {jug})**"),
                                                  file=arch,
                                                  view=VistaReiniciarCuatroEnLinea(
                                                        vista_maestra=self
                                                    )
                                                )

        self.mensaje_raiz = mens


    def refrescar_stats_cuatro_en_linea(self) -> None:
        """
        Refresca las estadísticas de cada jugador.
        """

        stats_base = self.registrador.stats_base()
        jug_1 = self.modelo.jugador_actual
        jug_2 = self.modelo.jugador_anterior

        _, vic1, emp1, der1 = self.registrador.get_datos(jug_1.id, stats_base)
        _, vic2, emp2, der2 = self.registrador.get_datos(jug_2.id, stats_base)

        if self.modelo.empate():
            emp1 += 1
            emp2 += 1
        else:
            vic1 += 1
            der2 += 1

        self.refrescar_datos(id_jugador=jug_1.id, victorias=vic1, empates=emp1, derrotas=der1)
        self.refrescar_datos(id_jugador=jug_2.id, victorias=vic2, empates=emp2, derrotas=der2)
