"""
Módulo para un juego de Ahorcado.
"""

from random import randint
from typing import TYPE_CHECKING, Optional, TypeAlias

from ...db.atajos import get_txt_juegos_path
from .partida_abc import JuegoBase

if TYPE_CHECKING:
    from ..jugador import ListaJugadores
    from ..opciones import OpcionesBase

FraseAhorcado: TypeAlias = list["LetraAhorcado"]

NUDO: str = "\U0001FAA2"


class LetraAhorcado:
    """
    Pequeña clase para representar la letra de una frase
    en el ahorcado.
    """

    def __init__(self, valor: str, oculta: bool) -> None:
        """
        Inicializa una instancia de tipo 'LetraAhorcado'.
        """

        if not isinstance(valor, str):
            raise TypeError(f"'{valor}' es de tipo '{type(valor).__name__}'." +
                            "Debería ser de tipo 'str'")

        if not len(valor) == 1:
            raise ValueError(f"'{valor}' debe ser un string de un (1) solo caracter")

        if not isinstance(oculta, bool):
            raise TypeError(f"Valor de 'oculta' ({oculta}) debería ser 'True' or 'False'.")

        self.valor = valor
        self._oculta = oculta


    def __str__(self):
        """
        Muestra la letra con su valor y si está oculta o no.
        Está pensado para fines de Debug.
        """

        return (f"<{self.valor}>" if self._oculta else self.valor)


    @property
    def oculta(self) -> bool:
        """
        Propiedad que funciona como wrapper para 'self._oculto'.
        """

        return self._oculta


    @oculta.setter
    def oculta(self, nuevo_valor: bool) -> None:
        """
        La letra, una vez descubierta, no debe poderse volver a cubrir.
        """

        if not nuevo_valor:

            self._oculta = nuevo_valor


class Ahorcado(JuegoBase):
    """
    Clase implementada para hacer un juego de ahorcado.
    """

    nombre_muestra: str = "Ahorcado"
    descripcion: str = "Adivina la frase antes de que se te acaben las vidas."
    emojis_muestra: tuple[str, ...] = (NUDO,)
    min_jugadores: int = 1
    max_jugadores: int = 8


    @staticmethod
    def cargar_palabra() -> str:
        """
        Devuelve una frase aleatoria a utilizar.
        """

        palabra = ""

        with open(f"{get_txt_juegos_path()}/palabras_ahorcado.txt", encoding="utf-8") as archivo:
            for _ in range(randint(0, 2**24)): # Número arbitrariamente alto.

                linea = archivo.readline()
                if not bool(linea): # final del archivo
                    archivo.seek(0)

                linea_mod = linea.rstrip("\n").strip()
                if bool(linea_mod):
                    palabra = linea_mod

        return palabra


    def __init__(self,
                 jugadores: "ListaJugadores",
                 opciones: Optional["OpcionesBase"]=None,
                 **kwargs) -> None:
        """
        Inicializa un juego.
        """

        super().__init__(jugadores, opciones, **kwargs)

        self.maximos_intentos: int = self.opciones.vidas
        self.intentos: int = self.maximos_intentos

        self.caracteres_usados: list[str] = []
        self.frase: FraseAhorcado = self._generar_frase(self.opciones.frase
                                                        if bool(self.opciones.frase)
                                                        else None)

        self._terminado: bool = False
        self._victoria: bool = False


    def __str__(self) -> str:
        """
        Dibuja el ahorcado en ASCII art para que pueda ser impreso.
        """

        frase = "  ".join([(letra.valor if not letra.oculta else '_') for letra in self.frase])

        caracteres_usados = (" - ".join(self.caracteres_usados) if self.caracteres_usados else '-')

        piezas = []

        simbolos = ('O', '|', '/', '\\', '|', '/', '\\')

        for i in range(6, -1, -1):
            piezas.append(simbolos[7 - (i + 1)] if self.intentos < (i + 1) else '')

        torso = (f"{piezas[2]} {piezas[1]} {piezas[3]}"
                 if (not piezas[2] and not piezas[3])
                 else (f"{piezas[2]}{piezas[1]}{piezas[3]}"))

        estado = f"""```
    
    -=-= AHORCADO =-=-

    +--------+
    |        |
    |        {piezas[0]}
    |       {torso}            {frase}
    |        {piezas[4]}
    |       {piezas[5]} {piezas[6]}
    |                       LETRAS USADAS: {caracteres_usados}
    |
==============           -= VIDAS RESTANTES: {self.intentos} =-
```"""
        return estado


    def _generar_frase(self, frase_preferida: Optional[str]=None) -> FraseAhorcado:
        """
        Genera la frase llena de letras.
        """

        frase = []

        for char in (frase_preferida
                     if frase_preferida is not None
                     else self.cargar_palabra()):
            frase.append(LetraAhorcado(char.upper(), bool(not char == ' ')))

        return frase


    def get_frase(self) -> str:
        """
        Devuelve una cadena de la frase.
        """

        return ''.join([char.valor for char in self.frase])


    def adivinar(self, char: str) -> tuple[bool, bool]:
        """
        Intenta adivinar una letra de ahorcado.
        Devuelve una tupla de dos valores booleanos, siendo el primero si
        la letra está en los caracteres usados, y el segundo si está en
        la frase.
        """

        if not len(char) == 1:
            raise ValueError(f"'{char}' debe ser una cadena de un (1) solo caracter")

        char = char.upper()
        fue_usado = char in self.caracteres_usados
        esta_presente = None
        apariciones = 0

        if not fue_usado:
            self.caracteres_usados.append(char)

        for letrita in self.frase:
            if letrita.valor == char:
                apariciones += 1
                letrita.oculta = False

        esta_presente = (apariciones > 0)
        if not esta_presente and not fue_usado:
            self.intentos -= 1

        return fue_usado, esta_presente


    def _refrescar_mensaje_ahorcado(self, extra: Optional[str]=None) -> None:
        """
        Refresca el mensaje a mostrar.
        """

        ex = ("" if extra is None else f"{extra}\n")
        self.mensaje = f"{ex}{str(self)}"


    def iniciar(self, *_args, **kwargs) -> bool:
        """
        Inicia el juego.
        """

        self._refrescar_mensaje_ahorcado()
        return True


    def actualizar(self, *_args, **kwargs) -> bool:
        """
        Actualiza el juego.
        """

        if self.terminado():
            return False

        letra = kwargs.get("letra").upper()
        fue_usado, es_correcta = self.adivinar(letra)

        if fue_usado:
            self._refrescar_mensaje_ahorcado(f"`{letra}` ya fue utilizada. Prueba otra.")
            return False

        if es_correcta:
            self._refrescar_mensaje_ahorcado(f"¡`{letra}` es **CORRECTA**!")
        else:
            self._refrescar_mensaje_ahorcado(f"`¡{letra}` es **INCORRECTA**!")

        self.termino_juego()

        return es_correcta


    def terminado(self) -> bool:
        """
        Determina si el juego está acabado.
        """

        return self._terminado


    def victoria(self) -> bool:
        """
        Determina si la partida termino en victoria.
        """

        if not self.terminado():
            return False

        return self._victoria


    def termino_juego(self) -> None:
        """
        Determina si la partida ha terminado, y si fue una victoria o derrota.
        """

        if self.intentos <= 0:
            self._terminado = True
            return

        for letra in self.frase:
            if letra.oculta:
                return

        self._terminado = True
        self._victoria = True


    def reiniciar(self) -> None:
        """
        Reinicia los parámetros del Ahorcado.
        """

        self.intentos = self.maximos_intentos

        self.caracteres_usados = []
        self.frase = self._generar_frase()

        self._terminado = False
        self._victoria = False

        self.iniciar()
        self.setup()
