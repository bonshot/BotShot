"""
Módulo que contiene la función creadora del registrador.
"""

from logging import INFO, FileHandler, Formatter, Logger, StreamHandler

from ..db.atajos import get_log_path


class BotLogger:
    """
    Registrador para el bot.
    """

    def __init__(self,
                 *,
                 nombre_log: str='botshot',
                 nivel_log: int=INFO,
                 formato='%(asctime)s - %(levelname)s - %(message)s',
                 formato_fecha='%d-%m-%Y %H:%M:%S') -> None:
        """
        Inicializa una instancia de 'BotLogger'.
        """

        super().__init__()

        self._formato: str = formato
        self._formato_fecha: str = formato_fecha

        self._formateador: Formatter = Formatter(fmt=self.formato, datefmt=self.formato_fecha)

        self.handler_archivos: FileHandler = FileHandler(filename=get_log_path(), encoding='utf-8')
        self.handler_consola: StreamHandler = StreamHandler()
        self.actualizar_formateador()

        self.logger = Logger(name=nombre_log)
        self.logger.setLevel(nivel_log)
        self.logger.addHandler(self.handler_archivos)
        self.logger.addHandler(self.handler_consola)


    def actualizar_formateador(self) -> None:
        """
        Actualiza el formateador del logger.
        """

        self.handler_archivos.setFormatter(self.formateador)
        self.handler_consola.setFormatter(self.formateador)


    @property
    def formateador(self) -> Formatter:
        """
        Devuelve el formateador del logger.
        """

        return self._formateador

    @formateador.setter
    def formateador(self, nuevo_formateador: Formatter) -> None:
        """
        Reemplaza el formateador actual por uno nuevo, y actualiza
        todos los handlers.
        """

        self._formateador = nuevo_formateador
        self.actualizar_formateador()


    @property
    def formato(self) -> str:
        """
        Devuelve el formato del logger.
        """

        return self._formato


    @formato.setter
    def formato(self, nuevo_formato: str) -> None:
        """
        Actualiza el formato del logger.
        """

        self._formato = nuevo_formato
        self.formateador = Formatter(fmt=self.formato, datefmt=self.formato_fecha)


    @property
    def formato_fecha(self) -> str:
        """
        Devuelve el formato de fecha del logger.
        """

        return self._formato_fecha


    @formato_fecha.setter
    def formato_fecha(self, nuevo_formato_fecha: str) -> None:
        """
        Actualiza el formato de fecha del logger.
        """

        self._formato_fecha = nuevo_formato_fecha
        self.formateador = Formatter(fmt=self.formato, datefmt=self.formato_fecha)


    def debug(self, mensaje: str, *args, **kwargs) -> None:
        """
        Registra un evento de nivel DEBUG.
        """

        self.logger.debug(mensaje, *args, **kwargs)


    def info(self, mensaje: str, *args, **kwargs) -> None:
        """
        Registra un evento de nivel INFO.
        """

        self.logger.info(mensaje, *args, **kwargs)


    def warning(self, mensaje: str, *args, **kwargs) -> None:
        """
        Registra un evento de nivel WARNING.
        """

        self.logger.warning(mensaje, *args, **kwargs)


    def error(self, mensaje: str, *args, **kwargs) -> None:
        """
        Registra un evento de nivel ERROR.
        """

        self.logger.error(mensaje, *args, **kwargs)


    def critical(self, mensaje: str, *args, **kwargs) -> None:
        """
        Registra un evento de nivel CRITICAL.
        """

        self.logger.critical(mensaje, *args, **kwargs)
