"""
Vista general de varias páginas.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from discord import Interaction
from discord import PartialEmoji as Emoji
from discord.enums import ButtonStyle, TextStyle
from discord.ui import Button, Modal, Select, TextInput, View, button

if TYPE_CHECKING:
    from discord import Message


class SaltarPagina(Modal):
    """
    Modal para seleccionar una página de una.
    """

    pagina: TextInput = TextInput(label="Página",
                                  style=TextStyle.short,
                                  custom_id="pg_select",
                                  placeholder="Escribe el número de página...",
                                  required=True,
                                  row=0)


    def __init__(self, paginador: "Paginador") -> None:
        """
        Inicializa una instancia de 'SaltarPagina'.
        """

        super().__init__(timeout=None,
                         title="Selecciona una página",
                         custom_id="pg_select_modal")

        self.paginador: "Paginador" = paginador


    def _es_int(self, num: str) -> bool:
        """
        Decide si un string representa un número entero.
        """

        try:
            int(num)
        except:
            return False
        else:
            return True


    async def on_submit(self, interaccion: Interaction) -> None:
        """
        Procesa la página descrita.
        """

        pag = self.pagina.value

        if self._es_int(pag) and 1 <= int(pag) <= self.paginador.max_paginas:
            self.paginador.pagina = int(pag) - 1 # Internamente empieza desde cero
            self.paginador.refrescar()
            await self.paginador.refrescar_mensaje(interaccion,
                                                   mensaje="Por favor elige un juego...")

        else:
            msg = f"*Número de página* `{pag}` *no válido.*"
            await self.paginador.refrescar_mensaje(interaccion,
                                                   mensaje=msg)


class Paginador(View):
    """
    Clase para seleccionar un juego que iniciar.
    """

    max_elementos_por_pagina: int = 20

    # Estos, por usarse fuera del scope de las funciones, son difíciles de cambiar en subclases
    fila_botones: int = 3
    id_atras: str = "pg_back"
    id_saltar: str = "pg_travel"
    id_adelante: str = "pg_next"


    def __init__(self,
                 elementos: Sequence,
                 /,
                 *,
                 mensaje_raiz: Optional["Message"]=None,
                 pagina: int=0,
                 timeout: Optional[float]=300.0) -> None:
        """
        Inicializa una instancia de 'Paginador'.
        """

        super().__init__(timeout=timeout)
        self._elementos: Sequence = elementos
        self.pagina: int = pagina

        self.mensaje_raiz: Optional["Message"] = mensaje_raiz

        self.refrescar()


    async def on_timeout(self) -> None:
        """
        El tiempo pasó.
        """

        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True


    @property
    def cantidad_elementos(self) -> int:
        """
        Devuelve la cantidad de elementos disponible en la página.
        """

        return (self.max_elementos_por_pagina
                if self.cantidad_lista_elementos > self.max_elementos_por_pagina
                else self.cantidad_lista_elementos)


    @property
    def cantidad_lista_elementos(self) -> int:
        """
        Devuelve la cantidad de juegos disponibles.
        """
        return len(self._elementos)


    @property
    def max_paginas(self) -> int:
        """
        Devuelve el límite de páginas a obedecer.
        Esto se usa para bloquear botones de ser necesario.
        """

        if not self.cantidad_elementos:
            return 0

        return ((self.cantidad_lista_elementos // self.cantidad_elementos) +
                (1 if self.cantidad_lista_elementos % self.cantidad_elementos else 0))


    def refrescar_extra(self) -> None:
        """
        Operaciones extra a realizar al refrescar, antes de actualizar botones.
        """

        return


    def refrescar(self) -> None:
        """
        Agrega el menú a la vista, y elimina el anterior, si había uno.
        """

        self.refrescar_extra()
        self.actualizar_botones()


    def actualizar_boton_extra(self, boton: Button) -> None:
        """
        Operaciones extra opcionales al actualizar un botón.
        """

        return


    def actualizar_boton(self, boton: Button) -> None:
        """
        Oculta el botón dependiendo de la página actual.
        """

        self.actualizar_boton_extra(boton)

        boton.disabled = any((
                (boton.custom_id == self.id_atras and self.pagina <= 0),
                (boton.custom_id == self.id_adelante and self.pagina >= (self.max_paginas - 1))
            )
        )

        if boton.custom_id == self.id_saltar:
            boton.label = f"{self.pagina + 1}/{self.max_paginas}"


    def actualizar_botones(self) -> None:
        """
        Desactiva los botones o no dependiendo en
        la página donde se está parado.
        """

        for item in self.children:
            if isinstance(item, Button):
                self.actualizar_boton(item)


    async def refrescar_mensaje(self,
                                interaccion: Interaction,
                                mensaje: Optional[str]=None) -> None:
        """
        Refresca el mensaje con una nueva vista.
        """

        if mensaje is None:
            await interaccion.response.edit_message(view=self)

        else:
            await interaccion.response.edit_message(content=mensaje,
                                                    view=self)


    @button(style=ButtonStyle.grey,
            custom_id=id_atras,
            row=fila_botones,
            emoji=Emoji.from_str("\U00002B05"))
    async def pagina_anterior(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Va a la página anterior.
        """
        self.pagina -= 1
        self.refrescar()
        await self.refrescar_mensaje(interaccion)


    @button(label=" / ", # Antes de mostrarse vacía, la vista lo actualiza una vez.
            style=ButtonStyle.grey,
            custom_id=id_saltar,
            row=fila_botones)
    async def pagina_saltar(self, interaccion: Interaction, _boton: Button) -> None:
        """
        El usuario quiere seleccionar una página en concreto.
        """

        await interaccion.response.send_modal(SaltarPagina(self))


    @button(style=ButtonStyle.grey,
            custom_id=id_adelante,
            row=fila_botones,
            emoji=Emoji.from_str("\U000027A1"))
    async def pagina_siguiente(self, interaccion: Interaction, _boton: Button) -> None:
        """
        Va a la página siguiente.
        """
        self.pagina += 1
        self.refrescar()
        await self.refrescar_mensaje(interaccion)

