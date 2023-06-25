"""
Módulo para un juego de Chinchón.
"""

from enum import Enum
from typing import TYPE_CHECKING, Optional, TypeAlias

from ..utils import Carta, Mazo
from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import ListaJugadores, Jugador
    from ..opciones import OpcionesBase

ListaCartas: TypeAlias = list[Carta]
Manos: TypeAlias = list["Mano"]

MADERA: str = "\U0001FAB5" # Hace las de 'Basto'
TROFEO: str = "\U0001F3C6" # Hace las de 'Copa'
DAGA: str = "\U0001F5E1" # Hace las de 'Espada'
MONEDA: str = "\U0001FA99" # Hace las de 'Oro'
COMODIN: str = "\U0001F0CF"
PALOS: tuple[str, ...] = (MADERA, TROFEO, DAGA, MONEDA, COMODIN)

EMOJIS_PALOS: dict[str, str] = {
    "BASTO": MADERA,
    "COPA": TROFEO,
    "ESPADA": DAGA,
    "ORO": MONEDA,
    "COMODIN": COMODIN
}


class Chinchon(JuegoBase):
    """
    Clase para implementar un juego de Chinchón.
    """

    nombre_muestra: str = "Chinchón"
    descripcion: str = "[NO TERMINADO] Vence a tus amigos en el clásico 'Chinchón' de la baraja española."
    emojis_muestra: tuple[str, ...] = PALOS
    min_jugadores: int = 2
    max_jugadores: int = 4


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        self.ronda: int = 0

        self.mazo: Mazo = Mazo(entero=True)
        self.descartes: Mazo = Mazo(entero=True, vacio=True)
        self.ind_primer_jugador_ronda: int = 0
        self.ind_jugador_actual: int = 0
        self.manos_jugadores: Manos = [Mano(jug) for jug in self.jugadores]
        self.cortador: Optional[Mano] = None

        self.posiciones: Manos = self.manos_jugadores.copy()

        if self.opciones is None:
            self.tope: int = 100
            self.hay_puntaje_negativo: bool = False
            self.admitir_reenganche: bool = True

        else:
            self.tope: int = self.opciones.tope
            self.hay_puntaje_negativo: bool = self.opciones.hay_puntaje_negativo
            self.admitir_reenganche: bool = self.opciones.admitir_reenganche

        self._terminado: bool = False


    @property
    def manos_en_juego(self) -> Manos:
        """
        Devuelve las manos que no fueron descalificadas
        o se reengancharon.
        """

        return [mano for mano in self.manos_jugadores
                if not mano.afuera]


    @property
    def cantidad_manos_jugando(self) -> int:
        """
        Devuelve la cantidad de manos actualmente jugando.
        """

        return len(self.manos_en_juego)


    @property
    def mano_actual(self) -> "Mano":
        """
        Devuelve la mano que está jugando.
        """

        return self.manos_en_juego[self.ind_jugador_actual]


    @property
    def mano_primera(self) -> "Mano":
        """
        Devuelve la mano del jugador que es 'Mano'.
        """

        return self.manos_en_juego[self.ind_primer_jugador_ronda]


    def es_mano_actual(self, mano: "Mano") -> bool:
        """
        Determina si una mano es la actual.
        """

        return mano == self.mano_actual


    def es_mano_primera(self, mano: "Mano") -> bool:
        """
        Determina si una mano es la primera del turno.
        """

        return mano == self.mano_primera


    @property
    def jugador_actual(self) -> "Jugador":
        """
        Devuelve el jugador actual.
        """

        return self.jugadores[self.ind_jugador_actual]


    def sig_ind_jugador(self) -> int:
        """
        Cambia el índice del jugador actual.
        """

        self.ind_jugador_actual = (self.ind_jugador_actual + 1) % self.cantidad_manos_jugando
        return self.ind_jugador_actual


    def sig_ind_jugador_ronda(self) -> int:
        """
        Cambia el índice del primer jugador de la ronda.
        """

        self.ind_primer_jugador_ronda = ((self.ind_primer_jugador_ronda + 1) 
                                         % self.cantidad_manos_jugando)
        self.ind_jugador_actual = self.ind_primer_jugador_ronda
        return self.ind_primer_jugador_ronda


    def es_ind_actual(self, ind: int) -> bool:
        """
        Verifica si un índice de jugador pertenece
        al actual.
        """

        return ind == self.ind_jugador_actual


    def hay_descartes(self) -> bool:
        """
        Indica si hay cartas en el mazo boca arriba.
        """

        return not self.descartes.vacio()


    def hay_cartas(self) -> bool:
        """
        Indica si hay cartas en el mazo boca abajo.
        """

        return not self.mazo.vacio()


    def ordenar_puntajes(self) -> None:
        """
        Ordena in-place las manos de los jugadores por su puntaje.
        """

        self.posiciones.sort(key=(lambda mano : mano.puntaje), reverse=False)


    def repartir_cartas(self) -> int:
        """
        Reparte cartas de un mazo nuevo a los jugadores,
        al principio de una ronda.
        """

        for _ in range(self.cantidad_manos_jugando):
            for _ in range(7):
                self.mano_actual.agregar_carta(self.mazo.get())

            # Queda igual porque la cantidad de vueltas es la cantidad de jugadores
            self.sig_ind_jugador()

        # Le da la octava carta al primer jugador
        self.mano_primera.agregar_carta(self.mazo.get())
        self.mano_primera.sig_estado()

        return len(self.mazo)


    def levantar_carta(self) -> Carta:
        """
        El jugador actual levanta una carta del mazo boca abajo.
        """

        carta = self.mazo.get()
        self.mano_actual.agregar_carta(carta)
        self.mano_actual.sig_estado()

        if self.mazo.vacio():
            self.mazo = self.descartes.copia()
            self.mazo.mezclar(10)
            self.descartes.vaciar()

        return carta


    def aportar_descarte(self, carta: Carta) -> None:
        """
        Pone la carta descartada encima de la pila de descartes.
        """

        self.descartes.put(carta, al_final=True)


    def levantar_descarte(self) -> Carta:
        """
        El jugador actual levanta una carta del mazo boca arriba.
        """

        carta = self.descartes.get()
        self.mano_actual.agregar_carta(carta)
        self.mano_actual.sig_estado()
        return carta


    def recuento_cartas(self) -> None:
        """
        Suma los puntos a todos los jugadores al finalizar una ronda.
        """

        if self.cortador is None or not isinstance(self.cortador, Mano):
            raise TypeError((f"La mano que corta debe ser de tipo {Mano.__name__!r}, " +
                             f"pero es de tipo {type(self.cortador).__name__!r}"))

        for mano in self.manos_en_juego:
            cartas = mano.cartas_que_suman()

            if not cartas and mano is self.cortador:
                if mano.chequear_chinchon():
                    self.hicieron_chinchon()
                else: # es un menos-diez
                    mano.puntaje -= 10
            else:
                self.contar_puntos(mano)

            if mano.puntaje >= self.tope:
                mano.descalificar()

        self.ordenar_puntajes()


    def hicieron_chinchon(self) -> None:
        """
        Recuento de puntajes en el caso de un chinchón.
        """

        for mano in self.manos_en_juego:
            if mano is not self.cortador:
                mano.puntaje += self.tope


    def contar_puntos(self, mano: "Mano") -> None:
        """
        Aplica los puntos a una mano.
        """

        for cart in mano.cartas_que_suman():
            if cart.es_comodin():
                mano.puntaje += 50
            else:
                mano.puntaje += cart.num


    def nueva_ronda(self) -> None:
        """
        Reinicia algunos parámetros para iniciar otra ronda.
        """

        if self.actualizar():
            self._terminado = True
            return

        self.ronda += 1
        self.sig_ind_jugador_ronda()
        self.cortador = None

        self.mazo: Mazo = Mazo(entero=True)
        self.descartes: Mazo = Mazo(entero=True, vacio=True)

        for mano in self.manos_en_juego:
            mano.vaciar_cartas()
            mano.estado = EstadoMano.INICIAL

        self.repartir_cartas()
        self.mensaje = "¡Iniciando nueva ronda!"


    def iniciar(self, *args, **kwargs) -> bool:
        """
        Inicia el juego.
        """

        self.mensaje = "¡Iniciando partida de Chinchón!"
        return True


    def actualizar(self, *args, **kwargs) -> bool:
        """
        Actualiza el juego.
        """

        return self.ganador() is not None


    def terminado(self) -> bool:
        """
        Determina si el juego está acabado.
        """

        return self._terminado


    def ganador(self) -> Optional["Mano"]:
        """
        Devuelve la mano ganadora de la partida, si la hay.
        """

        if self.cantidad_manos_jugando == 1:
            return self.manos_en_juego[0]

        elif self.cantidad_manos_jugando == 0:
            return self.posiciones[0]

        return None


class EstadoMano(Enum):
    """
    Enumeración de los posibles estados de
    una mano de Chinchón.
    """

    INICIAL = 0
    LEVANTO = 1
    DESCARTO = 2

    MOSTRADO = 3


class Mano:
    """
    Clase para implementar una mano de Chinchón.
    """

    def __init__(self, jugador: "Jugador") -> None:
        """
        Inicializa una instancia de 'Mano'.
        """

        self.jugador: "Jugador" = jugador
        self.afuera: bool = False
        self.reenganchado: bool = False
        self.estado: EstadoMano = EstadoMano.INICIAL
        self.cartas: ListaCartas = []
        self.puntaje: int = 0

        # Los grupos son agrupaciones de cartas en las que este modelo entiende
        # que están combinadas. Sin esto se entiende que el jugador quiere sumar
        # puntos.
        self.sueltas: ListaCartas = []
        self.grupo_1: ListaCartas = []
        self.grupo_2: ListaCartas = []


    @property
    def todos_los_grupos(self) -> list[ListaCartas]:
        """
        Devuelve todos los grupos registrados.
        """

        return [self.sueltas, self.grupo_1, self.grupo_2]


    @property
    def estado_inicial(self) -> bool:
        """
        Verifica si está en el estado INICIAL.
        """

        return self.estado == EstadoMano.INICIAL


    @property
    def estado_levanto(self) -> bool:
        """
        Verifica si está en el estado LEVANTO.
        """

        return self.estado == EstadoMano.LEVANTO


    @property
    def estado_descarto(self) -> bool:
        """
        Verifica si está en el estado DESCARTO.
        """

        return self.estado == EstadoMano.DESCARTO


    @property
    def estado_mostrado(self) -> bool:
        """
        Verifica si está en el estado MOSTRADO.
        """

        return self.estado == EstadoMano.MOSTRADO


    @property
    def cantidad_cartas(self) -> int:
        """
        Devuelve la cantidad de cartas en mano.
        """

        return len(self.cartas)


    def sig_estado(self) -> EstadoMano:
        """
        Reemplaza el estado de la mano por el siguiente.
        """

        if self.estado_inicial:
            self.estado = EstadoMano.LEVANTO

        elif self.estado_levanto:
            self.estado = EstadoMano.DESCARTO

        elif self.estado_descarto:
            self.estado = EstadoMano.INICIAL

        return self.estado


    def sin_cartas(self) -> bool:
        """
        Verifica si la mano no tiene cartas.
        """

        return self.cantidad_cartas == 0


    def vaciar_cartas(self) -> None:
        """
        Quita las cartas de todos los grupos.
        """

        self.cartas = []
        self.sueltas = []
        self.grupo_1 = []
        self.grupo_2 = []


    def descalificar(self) -> None:
        """
        Saca del juego a esta mano.
        """

        self.afuera = True


    def reengachar(self) -> None:
        """
        Reengancha a esta mano.
        """

        self.afuera = False
        self.reenganchado = True


    def agregar_carta(self, carta: Carta) -> None:
        """
        Agrega una carta a la mano.
        """

        self.cartas.append(carta)
        self.sueltas.append(carta)


    def _eliminar_carta(self,
                        carta: Carta,
                        grupo: ListaCartas,
                        suelto: bool=False) -> None:
        """
        Elimina definitivamente la carta de un grupo.

        'suelto' indica si debería comprobarse la integridad
        del grupo post-remove o si dejarlo tal cual.
        """

        self.cartas.remove(carta)
        grupo.remove(carta)
        if not suelto:
            self.verificar_grupo(grupo)


    def descartar(self, carta: Carta) -> int:
        """
        Descarta una carta que TIENE que estar en el grupo 1,
        el grupo 2, o en las sueltas (0).

        Se devuelve un entero indicando dicho estado.
        """

        for cart1 in self.grupo_1:
            if carta == cart1:
                self._eliminar_carta(carta, self.grupo_1, False)
                return 1

        for cart2 in self.grupo_2:
            if carta == cart2:
                self._eliminar_carta(carta, self.grupo_2, False)
                return 2

        self._eliminar_carta(carta, self.sueltas, True)
        return 0


    def verificar_grupo(self, grupo: ListaCartas, desagrupar: bool=True) -> bool:
        """
        Verifica si, al descartar una carta, se desbarata el grupo
        al no encaminarse ya a 'ligarse'.
        Un grupo de mismos números siempre está ligado.
        """

        cant_cartas = len(grupo)

        if (cant_cartas == 1 or
            len(set([cart.num for cart in grupo])) == 1): # Son todos los mismos números
            return True
        
        for i in range(cant_cartas - 1):
            act, sig = grupo[i], grupo[i + 1]
            if act.num != sig.num - 1:
                if desagrupar:
                    while grupo:
                        self.desagrupar(grupo[0], grupo_1=(grupo is self.grupo_1))
                return False

        return True


    def esta_descalificado(self, definitivamente: bool=False) -> bool:
        """
        Decide si una mano está fuera de juego.
        """

        return (self.afuera and
                (self.reenganchado if definitivamente else True))


    def tiene_suficientes_cartas(self) -> bool:
        """
        Una mano deberíta tener 7 (siete), o como mucho
        8 (ocho) cartas a la vez.
        """

        return self.cantidad_cartas in (7, 8)


    def apto_descarte(self) -> bool:
        """
        Verifica si la mano tiene 8 (ocho) cartas,
        y es apta para un descarte.
        """

        return self.cantidad_cartas == 8


    def indice_correcto(self, ind: int) -> bool:
        """
        Decide si un índice indicado está dentro de la mano.
        """

        return ind in range(self.cantidad_cartas)


    def cambiar(self, ind1: int, ind2: int) -> None:
        """
        Cambia de lugar dos cartas.
        """

        if (not self.tiene_suficientes_cartas() or
            not self.indice_correcto(ind1) or
            not self.indice_correcto(ind2)):
            return

        self.cartas[ind1], self.cartas[ind2] = self.cartas[ind2], self.cartas[ind1]


    def cartas_para_cortar(self) -> ListaCartas:
        """
        Devuelve las cartas aptas para poder cortar la ronda.
        """

        para_cortar = []

        for carta in self.sueltas:
            if (carta.es_comodin() or
                (carta.num > 5 and self.puntaje < 96)):
                continue

            para_cortar.append(carta)

        return para_cortar


    def agrupar(self, carta: Carta, grupo_1: bool=True, comodin_alto: bool=True) -> bool:
        """
        Intenta agregar una carta a los grupos de la mano.
        """

        grupo = (self.grupo_1 if grupo_1 else self.grupo_2)
        cant_cartas = len(grupo)

        if cant_cartas >= 4:
            return False

        for gr in self.todos_los_grupos:
            if carta in gr:
                grupo_origen = gr # Sí o sí uno tiene que ser
                break

        if cant_cartas == 0 or self.chequear_num(carta, grupo):
            return self.agregar_a_grupo(carta, grupo, grupo_origen, comodin_alto, False)

        if self.chequear_escalera(carta, grupo):
            return self.agregar_a_grupo(carta, grupo, grupo_origen, comodin_alto, True)

        return False


    def agregar_a_grupo(self,
                        carta: Carta,
                        grupo: ListaCartas,
                        grupo_origen: ListaCartas,
                        comodin_alto: bool,
                        por_escalera: bool) -> bool:
        """
        Agrega definitivamente una carta a los grupos de la mano.
        """

        if carta.es_comodin():
            if len(grupo) == 0:
                # Un comodín no puede ser la primera agregada a un grupo
                return False

            ord_num = (lambda cart: cart.num)
            esc = ((min(grupo, key=ord_num).num - 1)
                   if comodin_alto
                   else (max(grupo, key=ord_num).num + 1))
            num_val = grupo[0].num # Cualquiera del grupo debería servir
            carta.num = (esc if por_escalera else num_val)

        grupo.append(carta)
        grupo_origen.remove(carta)
        self.sortear_grupos()
        return True


    def desagrupar(self, carta: Carta, grupo_1: bool=True) -> None:
        """
        Quita una carta de uno de los grupos, y los devuelve a las sueltas.
        """

        grupo = self.grupo_1 if grupo_1 else self.grupo_2

        grupo.remove(carta)
        self.sueltas.append(carta)

        if carta.es_comodin():
            carta.num = None


    def chequear_num(self, carta: Carta, grupo: ListaCartas) -> bool:
        """
        Verifica si se puede meter una carta con el mismo número.
        """

        for cart in grupo:
            if ((not carta.es_comodin() and
                 (not carta.mismo_num(cart) or carta.mismo_palo(cart))) or
                # Hay dos comodines
                (carta.es_comodin() and carta.mismo_palo(cart))
            ):
                return False

        return True


    def chequear_escalera(self, carta: Carta, grupo: ListaCartas) -> bool:
        """
        Verifica si se puede meter una carta siguiendo una escalera.
        """

        for cart in grupo:
            if ((not carta.es_comodin() and
                 not cart.es_comodin() and
                 not carta.mismo_palo(cart)) or
                # Hay dos comodines
                (carta.es_comodin() and carta.mismo_palo(cart))
            ):
                return False

        prim, ult = grupo[0], grupo[-1]
        if not carta.es_comodin(): # Si es comodín a estas alturas se puede
            return (carta.es_anterior_a(prim) or
                    carta.es_posterior_a(ult))

        return True


    def chequear_chinchon(self) -> bool:
        """
        Verifica si la mano hizo un chinchón.

        Un chinchón ocurre cuando los grupos, combinados,
        forman una escalera de 7 cartas consecutivas del
        mismo palo y sin comodines.
        Tener un chinchón es victoria inmediata.
        """

        if (self.sueltas != [] or
            len(self.grupo_1) < 3 or
            len(self.grupo_1) < 3):
            return False

        mano_total = self.grupo_1 + self.grupo_2
        cant = len(mano_total) # Debería ser 7

        for i in range(cant - 1):
            act, sig = mano_total[i], mano_total[i + 1]
            if (not act.mismo_palo(sig) or
                act.num != sig.num - 1):
                return False

        return True


    def sortear_grupos(self) -> None:
        """
        Ordena los grupos, primero por número, luego por palo.
        """

        ord_num = (lambda cart: cart.num if cart.num is not None else 0)
        ord_pal = (lambda cart: cart.palo.value)

        for grupo in self.todos_los_grupos:
            grupo.sort(key=ord_num)
            grupo.sort(key=ord_pal)


    def cartas_que_suman(self) -> ListaCartas:
        """
        Crea una lista de cartas que no entraron a ningún grupo.
        """

        sumantes = []
        sumantes.extend(self.sueltas)

        grupos = [self.grupo_1, self.grupo_2]
        
        for i in range(len(grupos)):
            act, otro = grupos[i], grupos[i - 1]
            cant_act, cant_otro = len(act), len(otro)

            if (cant_act < 3 or
                # Si son justo 3 cartas, sí se puede formar un grupo
                (cant_act > 3 and cant_otro < 3)):
                sumantes.extend(act)
    
        return sumantes
