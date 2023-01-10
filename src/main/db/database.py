"""
Módulo de bases de datos.
"""

from os import PathLike
from sqlite3 import connect
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeAlias, Union

DictConds: TypeAlias = Dict[str, Any]
ValoresResolucion: TypeAlias = Literal["ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"]
_SingularResult: TypeAlias = Tuple[Union[None, int, str]]
FetchResult: TypeAlias = Union[List[_SingularResult], _SingularResult]

DEFAULT_DB: PathLike = "src/main/db/db.sqlite3"
RESOLUCIONES: Tuple[str, ...] = "ABORT", "FAIL", "IGNORE", "REPLACE", "IGNORE"


def crear_nueva_db(db_path: PathLike[str]="") -> None:
    """
    Crea una nueva db a partir de una plantilla.
    Esta NO será la db que BotShot use a menos que sea
    la del DEFAULT_DB.
    """

    db_path = db_path or DEFAULT_DB

    with connect(db_path) as con:
        cur = con.cursor()
        cur.executescript("""--sql
        
        CREATE TABLE propiedades (
            prop_id INTEGER PRIMARY KEY,
            nombre TEXT,
            valor TEXT
        ) STRICT;

        CREATE TABLE guilds (
            id INTEGER PRIMARY KEY,
            nombre TEXT
        ) STRICT;

        CREATE TABLE prefijos (
            id INTEGER PRIMARY KEY,
            id_guild INTEGER,
            prefijo TEXT,
            FOREIGN KEY(id_guild) REFERENCES guilds(id)
        ) STRICT;

        CREATE TABLE paths (
            id_path INTEGER PRIMARY KEY,
            nombre_path TEXT,
            fpath TEXT
        ) STRICT;

        CREATE TABLE canales_escuchables (
            id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            nombre TEXT,
            FOREIGN KEY(guild_id) REFERENCES guilds(id)
        ) STRICT;

        CREATE TABLE carpetas_recomendadas (
            id INTEGER PRIMARY KEY,
            recomendacion TEXT,
            nombre_usuario TEXT,
            id_usuario INTEGER
        ) STRICT;

        CREATE TABLE usuarios_autorizados (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            discriminador INTEGER
        ) STRICT;
        """)


def ejecutar_comando(comando: str, es_script: bool, db_path: PathLike[str]="") -> None:
    """
    Ejecuta un comando arbitrario, pasándolo tal cual a
    sqlite para parsear.
    """

    with connect(db_path) as con:
        cur = con.cursor()

        if es_script:
            cur.executescript(comando)
        else:
            cur.execute(comando)


def ejecutar_linea(comando: str, db_path: PathLike[str]="") -> None:
    """
    Ejecuta un comando de SQL que no requiera sacar datos.
    """

    ejecutar_comando(comando, False, db_path or DEFAULT_DB)


def ejecutar_script(comando: str, db_path: PathLike[str]="") -> None:
    """
    Ejecuta un comando de SQL de varias líneas.
    """

    ejecutar_comando(comando, True, db_path or DEFAULT_DB)


def _condiciones_where(**condiciones: DictConds) -> str:
    "Crea una expresión SQL con todas las condiciones en el kwargs."

    extra = None

    try:
        extra = condiciones.pop("where")
        if not isinstance(extra, tuple):
            raise TypeError("condiciones extra del parametro 'where' deben ser una tupla de strings.")
    except KeyError:
        extra = tuple()

    conds = " AND ".join([f"{k}={v!r}" for k, v in condiciones.items()] + list(extra))
    return ('' if not conds else f" WHERE {conds}")


def _protocolo_resolucion(resolucion: Optional[ValoresResolucion]=None) -> str:
    "Parsea una opcion para definir un protocolo en caso de que una operacion falle."

    if resolucion is None:
        res_protocol = ''
    elif resolucion.upper() not in RESOLUCIONES:
        raise ValueError(f"Tipo de resolucion debe ser uno de {RESOLUCIONES}")
    else:
        res_protocol = f" OR {resolucion} "

    return res_protocol


def sacar_datos_de_tabla(tabla: str,
                         sacar_uno: bool=False,
                         **condiciones: DictConds) -> FetchResult:
    "Saca datos de una base de datos."

    res = None
    conds = _condiciones_where(**condiciones)

    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {tabla}{conds};")
        res = (cur.fetchone() if sacar_uno else cur.fetchall())

    return res


def borrar_datos_de_tabla(tabla: str,
                          **condiciones: DictConds) -> None:
    """
    Borra datos de una base de datos.

    * NO oncluye una opción LIMIT.
    """

    conds = _condiciones_where(**condiciones)

    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM {tabla}{conds};")


def insertar_datos_en_tabla(tabla: str,
                            resolucion: Optional[ValoresResolucion]=None,
                            *,
                            llave_primaria_por_defecto: bool=True,
                            valores=Tuple[Any, ...]) -> None:
    "Intenta insertar datos en una tabla."

    protocolo_res = _protocolo_resolucion(resolucion)
    valores_wrapped = [f"{v!r}" for v in valores]
    valores_finales = f"({'?, ' if llave_primaria_por_defecto else ''}{', '.join(valores_wrapped)})"

    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.executescript(f"INSERT{protocolo_res} INTO {tabla} VALUES{valores_finales};")


def actualizar_dato_de_tabla(tabla: str,
                              resolucion: Optional[ValoresResolucion]=None,
                              *,
                              nombre_col: str,
                              valor: Any,
                              **condiciones: DictConds) -> None:
    "Actualiza un dato ya presente en tablas."

    if not isinstance(nombre_col, str):
        raise TypeError("El nombre de la columna debe ser de tipo string.")

    conds = _condiciones_where(**condiciones)
    res_protocol = _protocolo_resolucion(resolucion)

    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.execute(f"UPDATE{res_protocol} {tabla} SET {nombre_col}={valor!r} {conds};")


def existe_dato_en_tabla(tabla: str,
                         **condiciones: DictConds) -> bool:
    "Se fija si existe un dato coincidente en la tabla especificada."

    return bool(sacar_datos_de_tabla(tabla, **condiciones))
