"""
Módulo para la vista de una partida de Chinchón.
"""

from io import BytesIO
from random import randint
from typing import TYPE_CHECKING, Generator, Optional, TypeAlias, Union

from discord import File, Interaction
from discord.ui import Button, Select, View
from discord.enums import ButtonStyle
from PIL.Image import Image
from PIL.Image import new as img_new
from PIL.Image import open as img_open
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

from ....db.atajos import (get_cartas_espaniolas_path,
                           get_dorso_carta_espaniola_path,
                           get_mesa_cartas_path, get_minecraftia_font,
                           get_plantilla_carta_espaniola_path)
from ...excepciones import CantidadDeJugadoresIncorrecta
from ..vista_juego_abc import VistaJuegoBase
from .controles_chinchon import (BotonAgregarAGrupo, BotonCerrarChinchon,
                                 BotonCortar, BotonDescartarCarta,
                                 BotonLevantarCarta, BotonLevantarDescarte,
                                 BotonMostrarCartas, BotonQuitarDeGrupo, BotonSiguienteRonda,
                                 BotonTerminarTurno, OrganizarCartas)

if TYPE_CHECKING:
    from discord import Message, User
    from discord.ui import Item

    from ....botshot import BotShot
    from ...modelos import Carta, JuegoBase, ListaCartas, Mano
    from ...registradores import RegistradorBase
    from ...utils import Mazo
    from .controles_chinchon import (MenuAgregarAGrupo, MenuCortar,
                                     MenuDescartarCarta, MenuQuitarDeGrupo)

BarajaCoordsSpecs: TypeAlias = list[tuple[float, tuple[int, int], tuple[int, int]]]


class VistaChinchon(VistaJuegoBase):
    """
    Vista de Chinchón.
    """

    @staticmethod
    def agregar_boton_cerrar() -> bool:
        """
        Decide si agregar un botón para cerrar la vista.
        """

        return False


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
        
        with img_open(get_mesa_cartas_path()) as im:
            self.img_base: Image = im.copy()


    async def setup(self) -> None:
        """
        Da inicio al juego.
        """

        self.usuarios: list["User"] = []
        self.hijas: list[VistaChinchonPrivada] = []

        self.modelo.repartir_cartas()

        msg = self.modelo.mensaje

        for i, jug in enumerate(self.modelo.jugadores):
            usuario = await self.bot.fetch_user(int(jug.id))
            vista = VistaChinchonPrivada(self, i)
            mens = await usuario.send(content=msg,
                                      view=vista)
            vista.mensaje_raiz = mens
            await vista.setup()

            self.usuarios.append(usuario)
            self.hijas.append(vista)

        await self.refrescar_mensaje()
        await self.activar_btn_cerrar()
        


    @property
    def mano_w(self) -> int:
        """
        El ancho de una sub-imagen de baraja.
        """

        return int(self.img_base.width * 0.4)


    @property
    def mano_h(self) -> int:
        """
        El alto de una sub-imagen de baraja.
        """

        return int(self.img_base.height * 0.25)


    @property
    def perfil_size(self) -> int:
        """
        El ancho/alto de una imagen de perfil.
        """

        return int(self.mano_h * 0.5)


    @property
    def mano_borde_w(self) -> int:
        """
        Los bordes horizontales de la sub-imagen de una baraja.
        """

        return int(self.mano_w * 0.1)


    @property
    def mano_borde_h(self) -> int:
        """
        Los bordes verticales de la sub-imagen de una baraja.
        """

        return int(self.mano_h * 0.1)


    @property
    def mano_ang(self) -> float:
        """
        El ángulo de apertura de una baraja sostenida.
        """

        return 25.0


    @staticmethod
    def d_ang(num: int,
              ang: float=45.0,
              pres: int=5,
              rel_tol: float=0.05) -> Generator[float, None, None]:
        """
        Va cediendo los ángulos necesarios para rotar
        una mano de cartas.
        """

        act = ang
        dang = (2 * ang) / (num - 1)

        while act >= (-ang - rel_tol):
            cand = round(act, pres)
            yield (cand if abs(cand) > rel_tol else 0.0)
            act = round(act - dang, pres)


    @staticmethod
    def d_num(num: int) -> Generator[int, None, None]:
        """
        Va cediendo valores por los que calcular translaciones.
        """

        for i in range(num):
            mitad = num // 2
            cand = i - mitad
            if (cand >= 0) and (num % 2 == 0):
                yield cand + 1
            else:
                yield cand


    def coords_barajas(self) -> BarajaCoordsSpecs:
        """
        Denota, según el número de jugadores, una lista de tuplas
        en las que:
        
        El primer elemento es la rotación total a aplicarle a la
        mano entera.

        El segundo elemento es una tupla de dos enteros, denotando
        las coordenadas de la esquina superior izquierda de la mano,
        donde éste sería trasladada.

        Un  tercer elemento consta de una tupla de enteros, denotando
        las coordenadas de una foto de perfil.
        """

        cant = self.modelo.cantidad_jugadores
        min_jug = self.modelo.min_jugadores
        max_jug = self.modelo.max_jugadores

        if cant not in range(min_jug, max_jug + 1):
            raise CantidadDeJugadoresIncorrecta((f"Cantidad de jugadores {cant} es inválida." +
                                                 f"Debe ser un valor entre {min_jug} y " +
                                                 f"{max_jug}."))

        base_w, base_h = self.img_base.size
        mid_base_w = base_w // 2
        mid_base_h = base_h // 2
        mid_mano_w = self.mano_w // 2
        tamanio_perfil = int(self.perfil_size * 1.5)
        espacio_perfil = (tamanio_perfil - self.perfil_size)

        abajo_coords = (
            0.0,
            (mid_base_w - mid_mano_w, base_h - self.mano_h),
            (mid_base_w - mid_mano_w - tamanio_perfil, base_h - int(self.mano_h * 0.85))
        )
        izquierda_coords = (
            90.0,
            (0, mid_base_h - mid_mano_w),
            (int(self.mano_h * 0.15), mid_base_h - mid_mano_w - tamanio_perfil)
        )
        derecha_coords = (
            270.0,
            (base_w - self.mano_h, mid_base_h - mid_mano_w),
            (base_w - int(self.mano_h * 0.85), mid_base_h - mid_mano_w, - tamanio_perfil)
        )
        arriba_coords = (
            180.0,
            (mid_base_w - mid_mano_w, 0),
            (mid_base_w + mid_mano_w + espacio_perfil, int(self.mano_h * 0.45))
        )

        if cant == 2:
            return [abajo_coords,
                    arriba_coords]
        
        if cant == 3:
            return [abajo_coords,
                    izquierda_coords,
                    derecha_coords]
        
        elif cant == 4:
            return [abajo_coords,
                    izquierda_coords,
                    derecha_coords,
                    arriba_coords]


    def _carta_path(self, carta: "Carta") -> str:
        """
        Consigue el camino de la imagen de una carta.
        """

        num = (f"-{carta.num}"
               if not carta.es_comodin()
               else "")
        palo = carta.palo.value.lower()
        return f"{get_cartas_espaniolas_path()}/{palo}/{palo}{num}.png"


    def imagen_mano(self,
                    cartas: "ListaCartas",
                    *,
                    ocultas: bool=False,
                    ancho: Optional[int]=None,
                    angulo: Optional[float]=None) -> Image:
        """
        Genera una sub-imagen de una baraja.
        """

        ancho = ancho or self.mano_w
        alto = self.mano_h
        angulo = angulo or self.mano_ang
        cartas_num = len(cartas)

        img = img_new("RGBA", (ancho, alto))

        ancho_real = (ancho - 2 * self.mano_borde_w)
        dx = ancho_real // cartas_num

        angs = [a for a in self.d_ang(cartas_num, angulo)]
        trans_y = [abs(num) * 9 for num in self.d_num(cartas_num)]

        for i in range(cartas_num):
            cx = (((2 * i) + 1) * dx) // 2

            if not ocultas:
                carta_path = self._carta_path(cartas[i])
            else:
                carta_path = get_dorso_carta_espaniola_path()

            img_cart = img_open(carta_path).copy().rotate(angs[i], expand=True)
            cart_w = img_cart.height
            dy = (trans_y[i] if angulo != 0.0 else 0)

            coord = (self.mano_borde_w + (cx - (cart_w // 2)),
                     self.mano_borde_h + dy)
            img.alpha_composite(img_cart, coord)

        return img


    def generar_imagen_mazo(self, mazo: "Mazo", con_numero: bool=True) -> Image:
        """
        Genera la imagen del mazo boca-abajo.
        """

        cant = len(mazo)
        lim = 5
        dy = 6 # en pixeles
        esp_x, esp_y = 10, 10
        esp_num = ((dy * lim) * 2 if con_numero else 0)

        with img_open(get_dorso_carta_espaniola_path()) as dorso_im:
            img_dorso = dorso_im.copy()
        
        img_mazo = img_new("RGBA",
                           (img_dorso.width + esp_x,
                            img_dorso.height + esp_y + (dy * lim) + esp_num))

        for i in range(cant if cant < lim else lim):
            dorso = img_dorso.copy()
            img_mazo.alpha_composite(dorso, ((esp_x // 2), (esp_y // 2) + esp_num + (dy * i)))        

        if con_numero:
            dr = Draw(img_mazo)
            fuente = truetype(get_minecraftia_font(), size=int(img_dorso.height * 0.15))

            dr.text(((esp_x // 2) + (img_mazo.width // 2), (esp_y // 2)),
                    str(cant),
                    fill="#FFFFFF",
                    font=fuente,
                    anchor="mt", # medio-arriba
                    align="center")

        return img_mazo


    def generar_imagen_descartes(self,
                                 descartes: "Mazo",
                                 d_ang: int=10,
                                 cortado: bool=False) -> Image:
        """
        Genera la imagen del mazo boca-arriba
        """

        d_ang = abs(d_ang)
        lim = 5
        esp_x, esp_y = 30, 30

        with img_open(get_plantilla_carta_espaniola_path()) as im_plantilla:
            cart_w, cart_h = im_plantilla.size

        img_descartes = img_new("RGBA",
                                (cart_w + 2 * esp_x,
                                 cart_h + 2 * esp_y))

        with descartes.ver_primeras(lim, inverso=True) as cartas:
            cant = len(cartas)
            for i, cart in enumerate(cartas):
                if cortado and (i == (cant - 1)):
                    img_cart = img_open(get_dorso_carta_espaniola_path()).copy()
                else:
                    img_cart = img_open(self._carta_path(cart)).copy()
                randang = randint(-d_ang, d_ang)
                img_cart = img_cart.rotate(randang, expand=True)
                img_descartes.alpha_composite(img_cart,
                                              (esp_x // 2, esp_y // 2))

        return img_descartes


    async def generar_imagen_juego(self,
                                   *,
                                   modo_espectador: bool,
                                   perspectiva: int=0,
                                   descartes_cortado: bool=False,
                                   termino_ronda: bool=False) -> Image:
        """
        Genera la imagen con una perspectiva dada.
        """

        img = self.img_base.copy()
        cant_manos = len(self.modelo.manos_jugadores)
        mano_coords = self.coords_barajas()

        fuente = truetype(get_minecraftia_font(), size=int(img.height * 0.027))

        for i in range(cant_manos):
            ind = (perspectiva + i) % cant_manos
            mano: "Mano" = self.modelo.manos_jugadores[i]
            jug = mano.jugador
            mano_rot, (mano_x, mano_y), (perfil_x, perfil_y) = mano_coords[ind]

            with img_open((jug.foto_perfil
                           if jug.foto_perfil is not None
                           else await self.bot.fetch_avatar(int(jug.id)))) as im_perfil:
                # Si es una foto de discord, o si un jugador se guardó una miagen que no es PNG,
                # al abrirlo se pone en modo RGB, hay que convertirlo a RGBA
                img_perfil = im_perfil.copy()\
                             .convert("RGBA")\
                             .resize((self.perfil_size, self.perfil_size))
            if not mano.afuera:
                if termino_ronda:
                    esta_oculta = False
                elif modo_espectador:
                    esta_oculta = True
                else:
                    esta_oculta = (i != perspectiva)
                img_cart = self.imagen_mano(mano.cartas,
                                            ocultas=esta_oculta).rotate(mano_rot,
                                                                        expand=True)
                img.alpha_composite(img_cart, (mano_x, mano_y))
            img.alpha_composite(img_perfil, (perfil_x, perfil_y))

            dr = Draw(img)
            dr.text((perfil_x + (self.perfil_size // 2), perfil_y - (self.perfil_size * 0.2)),
                    f"{jug.nombre} ({mano.puntaje})",
                    fill="#FFFFFF",
                    font=fuente,
                    anchor="mm", # medio-medio
                    align="center")

        mazo_x, mazo_y = int(img.width * 0.525), int(img.height * 0.4)
        desc_x, desc_y = int(img.width * 0.4), mazo_y + int(img.height * 0.015)
        img.alpha_composite(self.generar_imagen_mazo(self.modelo.mazo),
                            (mazo_x, mazo_y))
        img.alpha_composite(self.generar_imagen_descartes(self.modelo.descartes,
                                                          d_ang=10,
                                                          cortado=descartes_cortado),
                            (desc_x, desc_y))

        return img


    async def generar_imagen_espectador(self, cortado: bool=False, termino: bool=False) -> Image:
        """
        Genera la imagen con cartas tapadas típica del
        cual ve la partida como espectador.
        """

        return await self.generar_imagen_juego(modo_espectador=True,
                                               descartes_cortado=cortado,
                                               termino_ronda=termino)


    def guardar_imagen(self,
                       im: Image,
                       modo_buffer: bool=False) -> Union[BytesIO, File]:
        """
        Procesa y guarda la imagen, devolviendo el archivo que la contiene.
        """

        arch = BytesIO()
        im.save(arch, format="PNG")
        arch.seek(0)

        return (arch if modo_buffer else File(arch, filename="img_chinchon.png"))


    async def generar_arch_espectador(self, cortado: bool=False, termino: bool=False) -> File:
        """
        Genera el archivo de la imagen desde la perspectiva de un espectador.
        """

        return self.guardar_imagen(await self.generar_imagen_espectador(cortado=cortado,
                                                                        termino=termino))


    async def refrescar_mensaje(self,
                                archivo: Optional[File]=None,
                                contenido: Optional[str]=None,
                                incluir_hijas: bool=False,
                                salvo: tuple["VistaChinchonPrivada", ...]=(),
                                cortado: bool=False,
                                termino: bool=False) -> None:
        """
        Renueva el mensaje raíz por otro.
        """

        archivo = archivo or await self.generar_arch_espectador(cortado=cortado, termino=termino)
        contenido = contenido or self.modelo.mensaje

        await self.mensaje_raiz.edit(content=contenido,
                                     attachments=[archivo],
                                     view=self)

        if not incluir_hijas:
            return

        for hija in self.hijas:
            if hija not in salvo:
                await hija.refrescar_mensaje(archivo=None,
                                             contenido=contenido,
                                             todos=False,
                                             cortado=cortado,
                                             termino=termino)


    async def activar_btn_cerrar(self) -> None:
        """
        Activa los botones de cerrar.
        """

        for hija in self.hijas:
            hija.boton_cerrar.disabled = False
            await hija.refrescar_solo_vista()


    async def desactivar_btn_cerrar(self) -> None:
        """
        Desctiva los botones de cerrar.
        """

        for hija in self.hijas:
            hija.boton_cerrar.disabled = True
            await hija.refrescar_solo_vista()


    async def final_juego(self) -> None:
        """
        Termina con el juego.
        """

        for hija in self.hijas:
            await hija.destruir(inmediatamente=True)

        ganador = self.modelo.ganador()
        lista_posiciones = []
        for pos, mano in enumerate(self.modelo.posiciones):
            lista_posiciones.append((f"- {pos + 1}. {mano.jugador.nombre}:\t " +
                                     f"**{mano.puntaje} pts.**"))
        pos_str = "\n".join(lista_posiciones)
        await self.mensaje_raiz.edit(content=(f"¡**{ganador.jugador.nombre}** es el ganador!" +
                                              f"\n\nPosiciones:\n\n>>>{pos_str}"),
                                     attachments=[],
                                     view=None)


    async def cerrar_juego(self) -> None:
        """
        Cierra el mensaje raíz y todos los sub-mensajes.
        """

        for hija in self.hijas:
            await hija.destruir()

        await self.mensaje_raiz.edit(content="*Cerrando partida...*",
                                     attachments=[],
                                     delete_after=5.0,
                                     view=None)


class VistaChinchonPrivada(View):
    """
    Vista privada de un chinchón, hecha para
    manipular el juego.
    """

    def __init__(self,
                 madre: "VistaChinchon",
                 indice_jugador: int,
                 mensaje_raiz: Optional["Message"]=None) -> None:
        """
        Inicializa la vista privada del Chinchón.
        """

        super().__init__(timeout=None)
        self.madre: "VistaChinchon" = madre
        self.ind: int = indice_jugador
        self.mano: "Mano" = self.madre.modelo.manos_en_juego[self.ind]
        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        self.boton_cerrar: BotonCerrarChinchon = BotonCerrarChinchon(self, True)
        self.add_item(self.boton_cerrar)

        # Organizar
        self.menu_organizar_cartas: Optional[OrganizarCartas] = None

        # Levantar
        self.boton_levantar_carta: Optional[BotonLevantarCarta] = None
        self.boton_levantar_descarte: Optional[BotonLevantarDescarte] = None

        # Descartar
        self.boton_descartar: Optional[BotonDescartarCarta] = None
        self.menu_descartar: Optional["MenuDescartarCarta"] = None

        # Terminar turno
        self.boton_terminar_turno: Optional[BotonTerminarTurno] = None

        # Grupos
        ## Grupo 1
        self.boton_agregar_grupo_1: Optional[BotonAgregarAGrupo] = None
        self.menu_agregar_grupo_1: Optional["MenuAgregarAGrupo"] = None
        self.boton_quitar_grupo_1: Optional[BotonQuitarDeGrupo] = None
        self.menu_quitar_grupo_1: Optional["MenuQuitarDeGrupo"] = None
        ## Grupo 2
        self.boton_agregar_grupo_2: Optional[BotonAgregarAGrupo] = None
        self.menu_agregar_grupo_2: Optional["MenuAgregarAGrupo"] = None
        self.boton_quitar_grupo_2: Optional[BotonQuitarDeGrupo] = None
        self.menu_quitar_grupo_2: Optional["MenuQuitarDeGrupo"] = None

        # Cortar
        self.boton_cortar: Optional[BotonCortar] = None
        self.menu_cortar: Optional["MenuCortar"] = None

        # Mostrar
        self.boton_mostrar: Optional[BotonMostrarCartas] = None

        # Ronda
        self.boton_sig_ronda: Optional[BotonSiguienteRonda] = None


    async def setup(self) -> None:
        """
        Acciones iniciales asincrónicas a realizar.
        """

        await self.refrescar_mensaje(await self.generar_arch_jugador(), inicial=True)


    @property
    def ind_str(self, zeros: int=2) -> str:
        """
        Da formato al índice con ceros delante.
        """

        return str(self.ind).zfill(zeros)


    async def refrescar_solo_vista(self,
                                   interaccion: Optional[Interaction]=None,
                                   mensaje: Optional[str]=None) -> None:
        """
        Refresca sólo la vista del mensaje (y quizás también el mensaje), no la imagen.
        """

        self.refrescar_items()

        dic = {"view": self}
        if mensaje is not None:
            dic.update({"content": mensaje})

        if interaccion is not None:
            await interaccion.response.edit_message(**dic)
            return

        await self.mensaje_raiz.edit(**dic)


    async def refrescar_mensaje(self,
                                archivo: Optional[File]=None,
                                contenido: Optional[str]=None,
                                inicial: bool=False,
                                interaccion: Optional[Interaction]=None,
                                diferida: bool=False,
                                todos: bool=False,
                                cortado: bool=False,
                                termino: bool=False) -> None:
        """
        Renueva el mensaje raíz.
        """

        archivo = archivo or await self.generar_arch_jugador(cortado=cortado, termino=termino)
        hay_interaccion = (interaccion is not None and isinstance(interaccion, Interaction))

        if not inicial:
            await self.madre.desactivar_btn_cerrar()

        contenido = contenido or self.madre.modelo.mensaje
        self.refrescar_items()

        if hay_interaccion and diferida:
            await interaccion.followup.edit_message(self.mensaje_raiz.id,
                                                    content=contenido,
                                                    attachments=[archivo],
                                                    view=self)
        else:
            if hay_interaccion:
                editar = interaccion.response.edit_message
            else:
                editar = self.mensaje_raiz.edit

                await editar(content=contenido,
                            attachments=[archivo],
                            view=self)

        if not inicial:
            await self.madre.activar_btn_cerrar()

        if todos:
            await self.madre.refrescar_mensaje(archivo=None,
                                               contenido=contenido,
                                               incluir_hijas=True,
                                               salvo=(self,),
                                               cortado=cortado,
                                               termino=termino)


    async def generar_imagen_jugador(self, cortado: bool=False, termino: bool=False) -> Image:
        """
        Genera la imagen con cartas tapadas salvo la
        del mismo jugador.
        """

        return await self.madre.generar_imagen_juego(modo_espectador=False,
                                                     perspectiva=self.ind,
                                                     descartes_cortado=cortado,
                                                     termino_ronda=termino)


    async def generar_arch_jugador(self, cortado: bool=False, termino: bool=False) -> File:
        """
        Genera un archivo con la imagen de la
        perspectiva de un jugador.
        """

        return self.madre.guardar_imagen(await self.generar_imagen_jugador(cortado=cortado,
                                                                           termino=termino))


    def refrescar_items(self) -> None:
        """
        Refresca los ítems de la vista.
        """

        for item in self.children:
            if isinstance(item, Button):
                self.refrescar_boton(item)
            elif isinstance(item, Select):
                self.refrescar_select(item)

        self.refrescar_item_extra()


    def refrescar_boton(self, boton: Button) -> None:
        """
        Refresca un botón.
        """

        if boton is self.boton_terminar_turno:
            boton.disabled = not self.mano.estado_descarto

        elif boton is self.boton_cortar:
            boton.disabled = (not bool(self.mano.cartas_para_cortar()) or
                              not self.mano.estado_levanto)


    def refrescar_select(self, menu: Select) -> None:
        """
        Refresca un menu selector.
        """

        ...


    def refrescar_item_extra(self) -> None:
        """
        Acciones particulares a realizar al refrescar items.
        """

        if self.mano.estado_mostrado:
            self._mano_mostrada()
            return

        if (self.boton_levantar_carta is None and
            self.mano.estado_inicial and
            self.madre.modelo.es_mano_actual(self.mano) and
            self.boton_mostrar is None):
            self.boton_levantar_carta = BotonLevantarCarta(self)
            self.add_item(self.boton_levantar_carta)
        
        if (self.boton_levantar_descarte is None and
            self.mano.estado_inicial and
            self.madre.modelo.es_mano_actual(self.mano) and
            self.boton_mostrar is None):
            self.boton_levantar_descarte = BotonLevantarDescarte(self)
            self.add_item(self.boton_levantar_descarte)

        if (self.boton_descartar is None and
            self.menu_descartar is None and
            self.menu_cortar is None and
            self.mano.apto_descarte() and
            self.boton_mostrar is None):
            self.boton_descartar = BotonDescartarCarta(self)
            self.add_item(self.boton_descartar)
        
        if self.menu_organizar_cartas is None:
            self.menu_organizar_cartas = OrganizarCartas(self)
            self.add_item(self.menu_organizar_cartas)
        else:
            self.menu_organizar_cartas.refrescar_opciones()

        if (self.boton_terminar_turno is None and
            self.madre.modelo.es_mano_actual(self.mano) and
            self.boton_mostrar is None):
            self.boton_terminar_turno = BotonTerminarTurno(self)
            self.add_item(self.boton_terminar_turno)

        if (self.boton_cortar is None and
            self.menu_cortar is None and
            self.menu_descartar is None and
            self.madre.modelo.es_mano_actual(self.mano) and
            self.mano.estado_levanto and
            self.boton_mostrar is None):
            self.boton_cortar = BotonCortar(self)
            self.add_item(self.boton_cortar)

        self._refrescar_items_grupos()


    def _refrescar_items_grupos(self) -> None:
        """
        Lógica para refrescar los botones y menús
        que interactúan con los grupos.
        """

        if (self.boton_agregar_grupo_1 is None and
            self.menu_agregar_grupo_1 is None and
            self.menu_quitar_grupo_1 is None):
            self.boton_agregar_grupo_1 = BotonAgregarAGrupo(self, grupo=1)
            self.add_item(self.boton_agregar_grupo_1)

        if (self.boton_agregar_grupo_2 is None and
            self.menu_agregar_grupo_2 is None and
            self.menu_quitar_grupo_2 is None):
            self.boton_agregar_grupo_2 = BotonAgregarAGrupo(self, grupo=2)
            self.add_item(self.boton_agregar_grupo_2)

        if (self.boton_quitar_grupo_1 is None and
            self.menu_agregar_grupo_1 is None and
            self.menu_quitar_grupo_1 is None):
            self.boton_quitar_grupo_1 = BotonQuitarDeGrupo(self, grupo=1)
            self.add_item(self.boton_quitar_grupo_1)

        if (self.boton_quitar_grupo_2 is None and
            self.menu_agregar_grupo_2 is None and
            self.menu_quitar_grupo_2 is None):
            self.boton_quitar_grupo_2 = BotonQuitarDeGrupo(self, grupo=2)
            self.add_item(self.boton_quitar_grupo_2)


    def _mano_mostrada(self) -> None:
        """
        Actualiza ítems cuando la mano ya fue mostrada.
        """

        if self.boton_sig_ronda is None:
            self.boton_sig_ronda = BotonSiguienteRonda(
                maestra=self.madre,
                mensaje="¿Siguiente ronda?",
                estilo=ButtonStyle.gray,
                custom_id=f"chinchon_next_round_btn_{self.ind}",
                emoji="\U000023ED",
                row=0
            )
            self.add_item(self.boton_sig_ronda)


    def eliminar_item(self, item: Optional["Item"]) -> bool:
        """
        Trata de eliminar un ítem de la vista.
        """

        estado = False

        if item is None:
            return estado

        for it in self.children:
            if it is item:
                self.remove_item(it)
                estado = True
                break

        for att in dir(self):
            if getattr(self, att) is item:
                setattr(self, att, None)
                estado = True
                break

        return estado


    async def destruir(self, inmediatamente: bool=False) -> bool:
        """
        Destruye, si puede, el mensaje raíz.
        """

        if self.mensaje_raiz is None:
            return False

        await self.mensaje_raiz.edit(content="*Acabando partida...*",
                                     attachments=[],
                                     delete_after=(None if inmediatamente else 5.0),
                                     view=None)
        return True
