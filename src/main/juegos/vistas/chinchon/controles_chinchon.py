"""
Módulo para componentes de control de la
vista de Chinchón.
"""

from typing import TYPE_CHECKING, Any, Literal, TypeAlias

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord import SelectOption
from discord.enums import ButtonStyle
from discord.ext.tasks import loop
from discord.ui import Button, Select

from ...modelos import EMOJIS_PALOS, EstadoMano
from ..auxiliar import BotonContador

if TYPE_CHECKING:
    from ...modelos import Mano
    from .vista_chinchon import VistaChinchonPrivada

IndGrupo: TypeAlias = Literal[1, 2]
IndTodosGrupos: TypeAlias = Literal[0, 1, 2]

CIRCULO_ROJO: str = "\U0001F534"
CIRCULO_AZUL: str = "\U0001F535"
ENGRANAJE: str = "\U00002699"

VOLVER: str = "\U000021A9"
VOLVER_LBL: str = "Volver"


def _generar_opciones_todas_cartas(mano: "Mano",
                                   salvo_grupos: tuple[IndTodosGrupos, ...]=()
    ) -> list[SelectOption]:
        """
        Genera las opciones de cartas.
        """

        opciones: list[SelectOption] = []
        grupos = []
        posibles_grupos = (mano.sueltas, mano.grupo_1, mano.grupo_2)
        for gr_ind in salvo_grupos:
            grupos.append(posibles_grupos[gr_ind])

        for i, carta in enumerate(mano.cartas):
            if any((carta in gr) for gr in grupos):
                continue

            if carta in mano.grupo_1:
                grupo = f"  {CIRCULO_ROJO}"
            elif carta in mano.grupo_2:
                grupo = f"  {CIRCULO_AZUL}"
            else:
                grupo = ""
            num = f"{carta.num} de " if not carta.es_comodin() else ""
            opciones.append(
                SelectOption(label=f"{num}{carta.palo.value}{grupo}",
                             value=str(i),
                             emoji=Emoji.from_str(EMOJIS_PALOS[carta.palo.value.upper()]))
            )

        return opciones


class BotonCerrarChinchon(Button):
    """
    Botón para cerrar la partida de Chinchón.
    """

    label_normal: str = "Cerrar"
    label_contando: str = "¿Seguro?"
    _cuenta_atras: int = 10

    def __init__(self,
                 vista: "VistaChinchonPrivada",
                 empezar_deshabilitado: bool=True) -> None:
        """
        Inicializa una instancia de 'BotonCerrarChinchon'.
        """

        self.vista: "VistaChinchonPrivada" = vista

        super().__init__(label=self.label_normal,
                         disabled=empezar_deshabilitado,
                         custom_id=f"chinchon_priv_close_{self.vista.ind_str}",
                         style=ButtonStyle.gray,
                         emoji=Emoji.from_str("\U0001F6D1"),
                         row=4)


    @loop(seconds=1, count=_cuenta_atras)
    async def confirmar_cerrar(self) -> None:
        """
        Confirma con una cuenta atrás si el usuario quiere cerrar.
        """

        i = self._cuenta_atras - self.confirmar_cerrar.current_loop
        self.label = f"{self.label_contando} ({i}s)"
        await self.vista.refrescar_solo_vista()


    @confirmar_cerrar.after_loop
    async def despues_de_cuenta(self) -> None:
        """
        Acciones posteriores a terminar la cuenta.
        """

        self.label = self.label_normal
        await self.vista.refrescar_solo_vista()


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Cierra la partida en todos los mensajes.
        """

        if self.confirmar_cerrar.is_running():
            self.confirmar_cerrar.stop()
            await interaccion.response.edit_message(content="*Cerrando Chinchón...*",
                                                    attachments=[],
                                                    view=None)
            await self.vista.madre.cerrar_juego()
        
        else:
            self.confirmar_cerrar.start()
            await self.vista.refrescar_solo_vista(interaccion)


class OrganizarCartas(Select):
    """
    Menú para intercambias posiciones de las cartas
    y así organizarlas mejor visualmente.
    """

    def __init__(self, vista: "VistaChinchonPrivada") -> None:
        """
        Inicializa el organizador de cartas.
        """

        self.vista: "VistaChinchonPrivada" = vista # Necesariamente primero

        super().__init__(custom_id=f"chinchon_organize_cards_{self.vista.ind_str}",
                         placeholder="Elige dos cartas para intercambiar de lugar",
                         min_values=2,
                         max_values=2,
                         options=_generar_opciones_todas_cartas(self.vista.mano),
                         disabled=False,
                         row=0)


    def refrescar_opciones(self) -> None:
        """
        Refresca las opciones del menú.
        """

        self.options = _generar_opciones_todas_cartas(self.vista.mano)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador eligió dos cartas para cambiar.
        """

        await interaccion.response.defer()

        cart1, cart2 = [int(val) for val in self.values]
        self.vista.mano.cambiar(cart1, cart2)
        self.refrescar_opciones()
        await self.vista.refrescar_mensaje(archivo=await self.vista.generar_arch_jugador(),
                                           contenido="¡Cartas cambiadas!",
                                           interaccion=interaccion,
                                           diferida=True)


class BotonDescartarCarta(Button):
    """
    Botón para descartar una carta cuando se tiene ocho.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el botón de descartar.
        """

        self.vista: "VistaChinchonPrivada" = vista

        super().__init__(style=ButtonStyle.blurple,
                         label="Descartar",
                         disabled=False,
                         custom_id=f"chinchon_discard_btn_{self.vista.ind_str}",
                         row=3)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador quiere descartar.
        """

        self.vista.eliminar_item(self)
        self.vista.eliminar_item(self.vista.boton_cortar)

        self.vista.menu_descartar = MenuDescartarCarta(self.vista)
        self.vista.add_item(self.vista.menu_descartar)
        await self.vista.refrescar_solo_vista(interaccion)


class MenuDescartarCarta(Select):
    """
    Menu selector para descartar una carta.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el menu selector de descartar.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.opcion_volver: SelectOption = SelectOption(label=VOLVER_LBL,
                                                        value=VOLVER_LBL,
                                                        description="Cancela la operación",
                                                        emoji=Emoji.from_str(VOLVER))

        super().__init__(custom_id=f"chinchon_discard_select_{self.vista.ind_str}",
                         placeholder="Elige una carta para descartar",
                         min_values=1,
                         max_values=1,
                         options=self._generar_opciones(),
                         disabled=False,
                         row=3)


    def refrescar_opciones(self) -> None:
        """
        Refresca las opciones del menú.
        """

        self.options = self._generar_opciones()


    def _generar_opciones(self) -> list[SelectOption]:
        """
        Genera una lista de cartas para elegir.
        """

        return [self.opcion_volver] + _generar_opciones_todas_cartas(self.vista.mano)


    def _volver(self) -> None:
        """
        Lógica para volver al menú anterior.
        """

        self.vista.eliminar_item(self)


    def descartar_carta(self, carta_ind: int) -> None:
        """
        Descarta definitivamente una carta.
        """

        carta = self.vista.mano.cartas[carta_ind]
        self.vista.mano.descartar(carta)
        self.vista.mano.sig_estado()
        self.vista.madre.modelo.aportar_descarte(carta)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador descarta una carta.
        """

        eleccion = self.values[0]
        self._volver()

        if eleccion == VOLVER_LBL:
            await self.vista.refrescar_solo_vista(interaccion)

        else:
            await interaccion.response.defer()

            self.vista.eliminar_item(self.vista.boton_cortar)

            self.descartar_carta(int(eleccion))

            await self.vista.refrescar_mensaje(contenido="¡Descarte hecho!",
                                               interaccion=interaccion,
                                               diferida=True,
                                               todos=True)


class BotonTerminarTurno(Button):
    """
    Botón para formalmente pasar el turno.
    """

    def __init__(self, vista: "VistaChinchonPrivada", empezar_deshabilitado: bool=True):
        """
        Inicializa el botón de terminar turno.
        """

        self.vista: "VistaChinchonPrivada" = vista

        super().__init__(style=ButtonStyle.gray,
                         label="Pasar turno",
                         disabled=empezar_deshabilitado,
                         custom_id=f"chinchon_end_turn_btn_{self.vista.ind_str}",
                         row=4)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Termina el turno formalmente.
        """

        await interaccion.response.defer()
        self.vista.eliminar_item(self)

        self.vista.mano.estado = EstadoMano.INICIAL
        self.vista.madre.modelo.sig_ind_jugador()

        jug = self.vista.madre.modelo.mano_actual.jugador
        msg = f"¡Ahora es el turno de `{jug.nombre}`!"
        await self.vista.refrescar_mensaje(contenido=msg,
                                           interaccion=interaccion,
                                           diferida=True,
                                           todos=True)


class BotonLevantarCarta(Button):
    """
    Botón para levantar una carta del mazo boca-abajo.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el botón de levantar cartas.
        """

        self.vista: "VistaChinchonPrivada" = vista

        super().__init__(style=ButtonStyle.gray,
                         label="Levantar del Mazo",
                         disabled=False,
                         custom_id=f"chinchon_take_card_btn_{self.vista.ind_str}",
                         row=3)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador levanta una carta.
        """

        await interaccion.response.defer()
        self.vista.eliminar_item(self.vista.boton_levantar_carta)
        self.vista.eliminar_item(self.vista.boton_levantar_descarte)

        self.vista.madre.modelo.levantar_carta()

        await self.vista.refrescar_mensaje(contenido="¡Carta levantada!",
                                           interaccion=interaccion,
                                           diferida=True,
                                           todos=True)


class BotonLevantarDescarte(Button):
    """
    Botón para levantar un descarte del mazo boca-arriba.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el botón de levantar descartes.
        """

        self.vista: "VistaChinchonPrivada" = vista

        deshabilitado = not self.vista.madre.modelo.hay_descartes()
        with self.vista.madre.modelo.descartes.ver_primeras(1) as cartas:
            if cartas:
                ult = cartas[0]
                ult_num = f"{ult.num} de " if not ult.es_comodin() else ""
                lbl = f"Levantar {ult_num}{ult.palo.value}"
            else:
                lbl = "No hay descartes"
        em = (Emoji.from_str(EMOJIS_PALOS[ult.palo.value.upper()])
              if not deshabilitado
              else None)

        super().__init__(style=ButtonStyle.gray,
                         label=lbl,
                         disabled=deshabilitado,
                         custom_id=f"chinchon_take_discarded_btn_{self.vista.ind_str}",
                         row=3,
                         emoji=em)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador levanta un descarte.
        """

        await interaccion.response.defer()
        self.vista.eliminar_item(self.vista.boton_levantar_carta)
        self.vista.eliminar_item(self.vista.boton_levantar_descarte)

        self.vista.madre.modelo.levantar_descarte()

        await self.vista.refrescar_mensaje(contenido="¡Descarte levantado!",
                                           interaccion=interaccion,
                                           diferida=True,
                                           todos=True)


class BotonAgregarAGrupo(Button):
    """
    Botón para agregar una carta a un grupo.
    """

    def __init__(self,
                 vista: "VistaChinchonPrivada",
                 *,
                 grupo: IndGrupo):
        """
        Inicializa el botón de quitar cartas de un grupo.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.ind_grupo: IndGrupo = grupo
        emoji = CIRCULO_ROJO if self.ind_grupo == 1 else CIRCULO_AZUL

        super().__init__(style=ButtonStyle.gray,
                         label="Agregar",
                         disabled=False,
                         custom_id=(f"chinchon_remove_from_group_{self.ind_grupo}" +
                                    f"_btn_{self.vista.ind_str}"),
                         emoji=Emoji.from_str(emoji),
                         row=self.ind_grupo)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador quiere agregar una carta a un grupo.
        """

        self.vista.eliminar_item(getattr(self.vista, f"boton_agregar_grupo_{self.ind_grupo}"))
        self.vista.eliminar_item(getattr(self.vista, f"boton_quitar_grupo_{self.ind_grupo}"))

        setattr(self.vista,
                f"menu_agregar_grupo_{self.ind_grupo}",
                MenuAgregarAGrupo(self.vista, grupo=self.ind_grupo))
        self.vista.add_item(getattr(self.vista, f"menu_agregar_grupo_{self.ind_grupo}"))

        await self.vista.refrescar_solo_vista(interaccion)


class MenuAgregarAGrupo(Select):
    """
    Menú para agregar una carta a un grupo.
    """

    def __init__(self,
                 vista: "VistaChinchonPrivada",
                 *,
                 grupo: IndGrupo):
        """
        Inicializa el menu selector de agregar cartas a un grupo.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.ind_grupo: IndGrupo = grupo
        self.comodin_alto: bool = True
        emoji = CIRCULO_ROJO if self.ind_grupo == 1 else CIRCULO_AZUL

        self.opcion_volver: SelectOption = SelectOption(label=VOLVER_LBL,
                                                        value=VOLVER_LBL,
                                                        description="Cancela la operación",
                                                        emoji=Emoji.from_str(VOLVER))

        super().__init__(custom_id=("chinchon_add_to_" +
                                    f"group_{self.ind_grupo}_{self.vista.ind_str}"),
                         placeholder=f"Agregar a grupo {emoji}",
                         min_values=1,
                         max_values=1,
                         options=self._generar_opciones(),
                         disabled=False,
                         row=self.ind_grupo)


    def _generar_opcion_comodin_alto(self) -> SelectOption:
        """
        Genera la opción extra de priorizar un comodín alto.
        """

        return SelectOption(
            label=f"Priorizar comodín {'alto' if self.comodin_alto else 'bajo'}",
            value=("False" if self.comodin_alto else "True"), # Deben ir al revés
            description=("Decide si, al agregar a un grupo, el comodín prioriza meterse al " +
                         "principio o al final de un grupo."),
            emoji=Emoji.from_str(ENGRANAJE)
        )


    def _generar_opciones(self) -> list[SelectOption]:
        """
        Genera las opciones de cartas.
        """

        return ([self.opcion_volver, self._generar_opcion_comodin_alto()] +
                _generar_opciones_todas_cartas(self.vista.mano,
                                               salvo_grupos=(self.ind_grupo,)))


    def _actualizar_opciones(self) -> None:
        """
        Actualiza las opciones de cartas.
        """

        self.options = self._generar_opciones()


    def _volver(self) -> None:
        """
        Lógica para volver al menú anterior.
        """

        self.vista.eliminar_item(self)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador agrega una carta a un grupo.
        """

        eleccion = self.values[0]
        msg = None

        if eleccion == VOLVER_LBL:
            self._volver()

        elif eleccion in ("True", "False"):
            self.comodin_alto = eval(eleccion)

        else:
            self._volver()
            carta = self.vista.mano.cartas[int(eleccion)]
            exito = self.vista.mano.agrupar(carta=carta,
                                            grupo_1=(self.ind_grupo == 1),
                                            comodin_alto=self.comodin_alto)
            msg = ("¡Se agregó una carta!"
                   if exito
                   else "*No se pudo agregar la carta.*")

        self._actualizar_opciones()
        await self.vista.refrescar_solo_vista(interaccion, msg)


class BotonQuitarDeGrupo(Button):
    """
    Boton para quitar una carta de un grupo.
    """

    def __init__(self,
                 vista: "VistaChinchonPrivada",
                 *,
                 grupo: IndGrupo):
        """
        Inicializa el botón de quitar cartas de un grupo.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.ind_grupo: IndGrupo = grupo
        emoji = CIRCULO_ROJO if self.ind_grupo == 1 else CIRCULO_AZUL

        super().__init__(style=ButtonStyle.gray,
                         label="Quitar",
                         disabled=False,
                         custom_id=(f"chinchon_add_to_group_{self.ind_grupo}" +
                                    f"_btn_{self.vista.ind_str}"),
                         emoji=Emoji.from_str(emoji),
                         row=self.ind_grupo)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador quiere quitar una carta de un grupo.
        """

        self.vista.eliminar_item(getattr(self.vista, f"boton_agregar_grupo_{self.ind_grupo}"))
        self.vista.eliminar_item(getattr(self.vista, f"boton_quitar_grupo_{self.ind_grupo}"))

        setattr(self.vista,
                f"menu_quitar_grupo_{self.ind_grupo}",
                MenuQuitarDeGrupo(self.vista, grupo=self.ind_grupo))
        self.vista.add_item(getattr(self.vista, f"menu_quitar_grupo_{self.ind_grupo}"))

        await self.vista.refrescar_solo_vista(interaccion)


class MenuQuitarDeGrupo(Select):
    """
    Menú selector para quitar una carta de un grupo.
    """

    def __init__(self,
                 vista: "VistaChinchonPrivada",
                 *,
                 grupo: IndGrupo):
        """
        Inicializa el menu selector de quitar cartas de un grupo.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.ind_grupo: IndGrupo = grupo
        emoji = CIRCULO_ROJO if self.ind_grupo == 1 else CIRCULO_AZUL

        self.opcion_volver: SelectOption = SelectOption(label=VOLVER_LBL,
                                                        value=VOLVER_LBL,
                                                        description="Cancela la operación",
                                                        emoji=Emoji.from_str(VOLVER))

        super().__init__(custom_id=("chinchon_remove_from_" +
                                    f"group_{self.ind_grupo}_{self.vista.ind_str}"),
                         placeholder=f"Quitar de grupo {emoji}",
                         min_values=1,
                         max_values=1,
                         options=self._generar_opciones(),
                         disabled=False,
                         row=self.ind_grupo)


    def _generar_opciones(self) -> list[SelectOption]:
        """
        Genera las opciones de cartas.
        """

        _demas_grupos: set[int] = {0, 1, 2}
        _demas_grupos.remove(self.ind_grupo)

        return ([self.opcion_volver] +
                _generar_opciones_todas_cartas(self.vista.mano,
                                               salvo_grupos=tuple(_demas_grupos)))


    def _actualizar_opciones(self) -> None:
        """
        Actualiza las opciones de cartas.
        """

        self.options = self._generar_opciones()


    def _volver(self) -> None:
        """
        Lógica para volver al menú anterior.
        """

        self.vista.eliminar_item(self)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador quita una carta de un grupo.
        """

        eleccion = self.values[0]

        if eleccion != VOLVER_LBL:
            carta = self.vista.mano.cartas[int(eleccion)]
            self.vista.mano.desagrupar(carta,
                                       grupo_1=(self.ind_grupo == 1))

        self._volver()
        self._actualizar_opciones()
        await self.vista.refrescar_solo_vista(interaccion)


class BotonCortar(Button):
    """
    Botón para cortar el mazo y acabar la ronda.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el botón de cortar el mazo.
        """

        self.vista: "VistaChinchonPrivada" = vista

        super().__init__(style=ButtonStyle.danger,
                         label="Cortar",
                         disabled=(not bool(self.vista.mano.cartas_para_cortar()) or
                                   not self.vista.mano.estado_levanto),
                         custom_id=f"chinchon_end_round_btn_{self.vista.ind_str}",
                         row=3)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        El jugador quiere cortar el mazo.
        """

        self.vista.eliminar_item(self)
        self.vista.eliminar_item(self.vista.boton_descartar)

        self.vista.menu_cortar = MenuCortar(self.vista)
        self.vista.add_item(self.vista.menu_cortar)

        await self.vista.refrescar_solo_vista(interaccion)


class MenuCortar(Select):
    """
    Menú selector para cortar el mazo.
    """

    def __init__(self, vista: "VistaChinchonPrivada"):
        """
        Inicializa el menu selector de cortar el mazo.
        """

        self.vista: "VistaChinchonPrivada" = vista
        self.opcion_volver: SelectOption = SelectOption(label=VOLVER_LBL,
                                                        value=VOLVER_LBL,
                                                        description="Cancela la operación",
                                                        emoji=Emoji.from_str(VOLVER))

        super().__init__(custom_id=f"chinchon_end_round_select_{self.vista.ind_str}",
                         placeholder="Elige una carta para cortar",
                         min_values=1,
                         max_values=1,
                         options=self._generar_opciones_cortar(),
                         disabled=False,
                         row=3)


    def _generar_opciones_cortar(self) -> list[SelectOption]:
        """
        Devuelve las cartas para cortar.
        """

        opciones: list[SelectOption] = []

        for i, carta in enumerate(self.vista.mano.cartas_para_cortar()):

            num = f"{carta.num} de " if not carta.es_comodin() else ""
            opciones.append(
                SelectOption(label=f"{num}{carta.palo.value}",
                             value=str(i),
                             emoji=Emoji.from_str(EMOJIS_PALOS[carta.palo.value.upper()]))
            )

        return [self.opcion_volver] + opciones


    def _volver(self) -> None:
        """
        Lógica para volver al menú anterior.
        """

        self.vista.eliminar_item(self)


    def _acabar_ronda(self) -> None:
        """
        Elimina los botones que no sean para terminar la ronda.
        """

        self.vista.eliminar_item(self.vista.boton_terminar_turno)
        tope = len(self.vista.madre.modelo.manos_en_juego)
        self.vista.madre.modelo.cortador = self.vista.mano

        for hija in self.vista.madre.hijas:
            hija.boton_mostrar = BotonMostrarCartas(
                maestra=self.vista.madre,
                mensaje="Mostrar Cartas",
                cantidad_tope=tope,
                estilo=ButtonStyle.blurple,
                custom_id=f"chinchon_show_cards_btn_{hija.ind_str}",
                row=3
            )
            hija.add_item(hija.boton_mostrar)


    def descartar_carta(self, carta_ind: int) -> None:
        """
        Descarta definitivamente una carta.
        """

        carta = self.vista.mano.cartas_para_cortar()[carta_ind]
        self.vista.mano.descartar(carta)
        self.vista.madre.modelo.aportar_descarte(carta)


    async def callback(self, interaccion: Interaction) -> Any:
        """
        Se corta la ronda.
        """

        eleccion = self.values[0]
        self._volver()

        if eleccion != VOLVER_LBL:
            await interaccion.response.defer()
            self.descartar_carta(int(eleccion))
            self._acabar_ronda()
            await self.vista.refrescar_mensaje(contenido="**¡Ronda acabada!**",
                                               interaccion=interaccion,
                                               diferida=True,
                                               todos=True,
                                               cortado=True,
                                               termino=False)
        else:
            await self.vista.refrescar_solo_vista(interaccion)


class BotonMostrarCartas(BotonContador):
    """
    Botón para mostrar cartas.
    """

    def jugador_existe(self, id_jugador: str) -> bool:
        """
        Verifica si un jugador existe entre los registrados.
        """

        for mano in self.maestra.modelo.manos_en_juego:
            if id_jugador == mano.jugador.id:
                return True

        return False


    async def actualizar_vista(self, interaccion: Interaction) -> None:
        """
        Refresca la vista.
        """

        for hija in self.maestra.hijas:
            if hija.boton_mostrar is None:
                continue

            hija.boton_mostrar.jugador_aceptar(str(interaccion.user.id))

            if hija.boton_mostrar is self:
                hija.boton_mostrar.label = hija.boton_mostrar.cambiar_mensaje("Apretado")
                await hija.refrescar_solo_vista(interaccion=interaccion)
            else:
                hija.boton_mostrar.label = hija.boton_mostrar.get_mensaje()
                await hija.refrescar_solo_vista(interaccion=None)

    async def accion(self) -> Any:
        """
        Realiza la acción del botón contador.
        """

        arch_espectador = await self.maestra.generar_arch_espectador(cortado=True,
                                                                     termino=True)
        msg = "¡Mostrando cartas!"

        for hija in self.maestra.hijas:
            for item in [hija.boton_mostrar,
                         hija.menu_organizar_cartas,
                         hija.boton_agregar_grupo_1,
                         hija.boton_quitar_grupo_1,
                         hija.boton_agregar_grupo_2,
                         hija.boton_quitar_grupo_2]:
                hija.eliminar_item(item)
            hija.mano.estado = EstadoMano.MOSTRADO

        self.maestra.modelo.recuento_cartas()
        await self.maestra.refrescar_mensaje(archivo=arch_espectador,
                                             contenido=msg,
                                             incluir_hijas=True,
                                             cortado=True,
                                             termino=True)


class BotonSiguienteRonda(BotonContador):
    """
    Botón para pasar a la siguiente ronda.
    """

    def jugador_existe(self, id_jugador: str) -> bool:
        """
        Verifica si un jugador existe entre los registrados.
        """

        for mano in self.maestra.modelo.manos_en_juego:
            if id_jugador == mano.jugador.id:
                return True

        return False


    async def actualizar_vista(self, interaccion: Interaction) -> None:
        """
        Refresca la vista.
        """

        for hija in self.maestra.hijas:
            if hija.boton_sig_ronda is None:
                continue

            hija.boton_sig_ronda.jugador_aceptar(str(interaccion.user.id))
            if hija.boton_sig_ronda is self:
                hija.boton_sig_ronda.label = hija.boton_sig_ronda.cambiar_mensaje("Aceptado")
                await hija.refrescar_solo_vista(interaccion=interaccion)
            else:
                hija.boton_sig_ronda.label = hija.boton_sig_ronda.get_mensaje()
                await hija.refrescar_solo_vista(interaccion=None)


    async def accion(self) -> Any:
        """
        Realiza la acción del botón contador.
        """

        for hija in self.maestra.hijas:
            hija.eliminar_item(hija.boton_sig_ronda)

        self.maestra.modelo.nueva_ronda()
        if self.maestra.modelo.terminado():
            await self.maestra.final_juego()
        else:
            await self.maestra.refrescar_mensaje(incluir_hijas=True)

