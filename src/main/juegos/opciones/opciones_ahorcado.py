"""
Módulo para las opciones del Ahorcado.
"""

from .opciones_abc import OpcionesBase


class OpcionesAhorcado(OpcionesBase):
    """
    Opciones del Ahorcado.
    """

    def __init__(self,
                 mensaje_inicial: str = "Viendo configuraciones del Ahorcado") -> None:
        """
        Inicializa las opciones del Ahorcado.
        """

        super().__init__(mensaje_inicial)

        self.vidas: int = 7
        self.frase: str = ""


    def propiedades(self) -> list:
        """
        Devuelve una lista de las propiedades de esta clase
        de opciones, apta para procesarlas con un paginador.
        """

        return [self.vidas, self.frase]


    def cambiar_vidas(self, nuevo_valor: int) -> int:
        """
        Intenta cambiar el valor de las vidas.
        """

        if nuevo_valor < 1:
            nuevo_valor = 1

        self.vidas = nuevo_valor
        return self.vidas


    def cambiar_frase(self, nueva_frase: str) -> str:
        """
        Cambia la frase por una nueva, y la devuelve.
        """

        self.frase = nueva_frase
        return self.frase


    def mas_vidas(self, mas: int=1) -> int:
        """
        Agrega 'mas' al contador de vidas.
        """

        self.vidas += abs(mas)
        return self.vidas


    def menos_vidas(self, menos=1) -> int:
        """
        Resta 'menos' al contador de vidas.

        No tiene efecto si el contador ya está en 1.
        """

        if (self.vidas - abs(menos)) >= 1:
            self.vidas -= abs(menos)

        return self.vidas
