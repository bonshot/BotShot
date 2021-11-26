# -= BotShot =-

<img alt="calamardo_guapo.png" align="left" src="extra/img/references/handsome_squidward_rtx_circle.png" height=128 width=128 />

<p align="left">
<img alt="version" src="https://img.shields.io/badge/version-0.0.1-brightgreen" />
<img alt="estrellas" src="https://img.shields.io/github/stars/bonshot/BotShot?label=Estrellas&style=social" />
<img alt="estrellas" src="https://img.shields.io/github/watchers/bonshot/BotShot?label=Visitas&style=social" />

Este bot está pensado para procesar imágenes ~~(en su mayoría +18)~~ y
almacenarlas en un directorio designado acorde.
</p>

<br/>
<br/>
<br/>

**Creado por:**
<p align="left">
<img align="left" src="https://github.com/NLGS2907.png" height=32 width=32 />

[Franco "NLGS" Lighterman Reismann](https://github.com/NLGS2907)
</p>

<p align="left">
<img align="left" src="https://github.com/bonshot.png" height=32 width=32 />

[Facundo "BonShot" Aguirre Argerich](https://github.com/bonshot)
</p>

<hr style="height:1px; width:35%" />

* **[Enlace de Invitación]()**

* **[Dependencias](requirements.txt)**

    - [python-dotenv](https://pypi.org/project/python-dotenv/)

    - [discord.py](https://pypi.org/project/discord.py/) (rama `master`)

* **[Licencia MIT](LICENSE)**

<br/>
<hr style="height:3px; width:50%" />
<br/>

## Índice

* [Convención del Código](#convención-del-código)

    - [Variables](#variables)

    - [Constantes](#constantes)

    - [Funciones](#funciones)

        - [Parámetros](#parámetros)

            - [Parámetros por Defecto](#parámetros-por-defecto)

    - [Clases](#clases)

    - [Archivos](#archivos)

        - [Carpetas](#carpetas)

    - [Cuerpo del Código](#cuerpo-del-código)

        - [Documentación](#documentación)

        - [Pistas de Tipo](#pistas-de-tipo)

<br/>
<hr style="height:3px; width:50%" />
<br/>

## Convención del Código

A continuación se detallan las convenciones a usar para el código de este
proyecto, de manera que se asegura un código más uniforme.

<hr style="height:2px; width:75%" />

### Variables

Para las variables, se debe escribir todo en minúscula, con barras bajas
("`_`")  como separación entre palabras, es decir que se debe seguir
`snake_case`, la cual coincide con la convención de python. ***Ejemplo:***
```python
listaDeNumeros = [1, 2, 3, 4, 5] # <-- Esto está mal
lista_de_numeros = [1, 2, 3, 4, 5] # <-- Esto está bien

# Después

>>> lista_de_numeros
[1, 2, 3, 4, 5]
```

A poder ser, el nombre de la variable debe ser un nombre descriptivo al
propósito de dicha variable.

<hr style="height:1px; width:50%" />

### Constantes

Las constantes, según se las puede considerar en el lenguaje Python, son
"variables" que cambian su valor a lo largo de la ejecución del programa. <br/>
Estas deben tener los nombres todo en mayúsculas, con las palabras siendo
separadas por una barra baja ("`_`"). ***Ejemplo:***
```python
MENSAJE_A_MOSTRAR = "¡Hola!"
"""
Pequeño mensaje a mostrar.
"""


def pruebas() -> None:
    """
    Imprime algunas pruebas.
    """
    print(f"Prueba 1:\t{MENSAJE_A_MOSTRAR}")
    print(f"Prueba 2:\tTe veo. {MENSAJE_A_MOSTRAR}")
    print(f"Prueba 3:\t{MENSAJE_A_MOSTRAR} ¿Cómo estás?")

# Después

>>> pruebas()
Prueba 1:   ¡Hola!
Prueba 2:   Te veo. ¡Hola!
Prueba 3:   ¡Hola! ¿Cómo estás?
```

Preferentemente, las constantes no deben ir pegadas, sino con
**una línea vacía** de por medio entre otras variables o constantes,
y **dos líneas vacías** de funciones, clases, métodos de clases o similar. <br/>
Las constantes también deben ser documentadas según la parte de [documentación](#documentación).

<hr style="height:1px; width:50%" />

### Funciones

Las funciones, más específicamente sus nombres, siguen una convención similar
a las [variables](#variables). ***Ejemplo:***
```python
def producto_dos_valores(x: int, y: int) -> int:
    """
    Devuelve el producto de dos números enteros.
    """
    return x * y
```

De nuevo, debe ser un nombre descriptivo. El código debe ser separado por
una nueva línea (sin líneas vacías de por medio), del punto donde termina la documentación de la función.<br/>
Dicha documentación (el *docstring*) sigue la convención descrita
en [documentación](#documentación).

<hr style="height:1px; width:25%" />

#### Parámetros

Nótese que en el ejemplo de [funciones](#funciones), la primera línea
contiene `x: int, y: int`. Los parámetros deben estar separados por una coma
seguida de un espacio ("`, `"), y con el formato `nombre=valor`, sin
espacios entre `nombre` y `valor`.

Las pistas de tipo como `: int` se explican mejor en [pistas de tipo](#pistas-de-tipo).

##### Parámetros por Defecto

Si un argumento no es especificado, la función trata de buscar el valor "por
defecto", si este está disponible. Los parámetros por defecto se definen
(valga la redundancia) en la "definición" de la función. ***Ejemplo:***
```python
def agregar_numero(lista: list[int], numero: int=5) -> list[int]:
    """
    Agrega un número al final de una lista de números enteros.
    """
    lista.append(numero)
    return lista

# Después

>>> lista_numeros = [1, 2, 3, 4]
>>> agregar_numero(lista_numeros, 4)
[1, 2, 3, 4, 4]
>>> agregar_numero(lista_numeros)
[1, 2, 3, 4, 5]
```

Como se ve, al no especificar `numero` se utiliza `5` por defecto.

**NOTA:** Al especificar parámetros por defecto, **NUNCA** se debe usar un
tipo de dato mutable, como las listas. Como los parámetros por defecto se
crean en la *definición* de la función, la referencia creada es la misma
para cada llamada a la función. ***Ejemplo:***
```python
def agregar_numero(numero: int=5, lista: list[int]=[]) -> list[int]:
    """
    Agrega un número al final de una lista de números enteros.
    """
    lista.append(numero)
    return lista

# Después

>>> lista_a = agregar_numero()
>>> lista_a
[5]
>>> lista_b = agregar_numero(4)
>>> lista_b
[5, 4]
```

Como se observa, en realidad `lista_a` y `lista_b` refieren a la misma lista,
que fue siendo referenciada en subsecuentes llamadas a la misma función, por
lo que si se quería crear dos listas distintas `[5]` y `[4]`, definirlo
en los parámetros por defecto no es la solución deseable. <br/>
En tal caso se puede lograr especificándolo como argumento:
```python
>>> lista_a = agregar_numero(4, [])
```

Así nos aseguramos de siempre crear una nueva.

<hr style="height:1px; width:50%" />

### Clases

Las clases deben tener todas las iniciales de palabras en mayúsculas, y el
resto mínusculas. No hay separación entre palabras (similar a `camelCase`).
***Ejemplo:***
```python
class FraccionNoEncontrada(Exception):
    """
    La excepción no fue encontrada
    """
    ...
```

Los **atributos** de las clases siguen la convención de [variables](#variables). <br/>
Los **métodos** de las clases siguen la convención de las [funciones](#funciones).

<hr style="height:1px; width:50%" />

### Archivos

Los archivos, obviando su extensión, siguen la convención de las [variables](#variables).

<hr style="height:1px; width:25%" />

#### Carpetas

A los efectos de este proyecto, dentro del directorio de imágenes a utilizar
se recomienda **NO** poner ningún tipo de archivo dentro de una carpeta que
tenga una subcarpeta (o carpeta "hija"). Es decir, sólo ponerlas en las
carpetas "hojas".

Cualquier otra carpeta fuera de este sub-directorio no sigue ninguna
convención para las carpetas, pero la de los archivos sigue aplicando.

<hr style="height:1px; width:50%" />

### Cuerpo del Código

Unas recomendaciones para tener el código más limpio:

* **Imports:** Al hacer `import`, tratar de agruparlo por módulo desde donde
se importa, dejando líneas vacías como separación.

* **Funciones:** Entre definiciones de funciones o métodos, o entre variables/constantes/imports y definiciones de funciones o métodos, debe
haber **dos (2) líneas vacías de separación**, según la convención de Python.

* **Bloques de Código:** Dentro del cuerpo de funciones, o cualquier otro
lado, se recomienda separar por **una (1) línea vacía** los bloques de código
de las otras variables o bloques. Por "bloques" entendemos, por ejemplo, el
cuerpo de los ciclos `for` o `while`.

* **Scripts:** Similarmente, para los scripts de Python donde se escriba
código, y la mayoría de archivos que no sean de texto plano, los mismos
deben terminar con **una (1) línea vacía**, también de acuerdo con la
convención de Python.

<hr style="height:1px; width:25%" />

#### Documentación

La documentación debe ser en forma de tres y tres comillas dobles ('`"`'),
y de forma en que el contenido del *docstring* que dentro esté separado por
nuevas líneas. ***Ejemplo:***
```python
MAIN_PATH = "src/main.py"
"""
Camino al módulo principal.
"""
```

Esto debe aplicar para:

* **Variables**

* **Constantes**

* **Funciones**

* **Clases**

    - **Métodos de Clase**

    - **Atributos de Clase**

* **Módulos**

En el caso de los módulos, el *docstring* debe ir arriba de todo, incluso
antes que los imports.

<hr style="height:1px; width:25%" />

#### Pistas de Tipo

A pesar de que el lenguaje Python es uno de tipado dinámico, además de ser
buena práctica, las pistas de tipo (del inglés "*type hints*" o
"*type hinting*") son útiles para indicar el tipo de los datos con los que
tratar y de evitar recurrir a los *docstrings* por la siguiente razón:

Este proyecto utiliza [discord.py](https://github.com/Rapptz/discord.py) de **Rapptz**. El mismo internamente tiene un *type checker* que implícitamente
convierte los tipos de datos dentro de funciones y demás, fueran éstos
no compatibles con los que las pistas de tipo dicen. <br/>
Se adopta pues la convención de usarlas para este proyecto, incluidas los
aliases y los tipos importados desde el módulo `typing`. ***Ejemplo:***
```python
def sumatoria(*valores: list[int]) -> int:
    """
    Suma todos los valores de una lista de números enteros entre sí.
    """
    suma = 0

    for valor in valores:
        suma += valor

    return suma

# Después

>>> sumatoria(5, 4, 2, 7, 6, 8)
32
```

Donde se ve que `valores` es una lista de enteros (`list[int]`) y viene en
el formato `dato: tipo` donde `dato` y `tipo` son separados por dos puntos
seguidos de un espacio ("`: `").
