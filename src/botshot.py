"""
Módulo destinado a contener las funciones del bot.
"""

from discord import Message, Guild
from discord.ext import commands
from datetime import datetime

import archivos

DEFAULT_PREFIX = '.'
"""
El prefijo por defecto, que se asigna cuando el bot ingresa
por primera vez a un server o cuando no es válida la opción querida.
"""

PREFIXES_FILE = 'src/prefixes.csv'

def get_prefijo(bot, mensaje: Message) -> str:
    """
    Se fija en el diccionario de prefijos y devuelve el que
    corresponda al servidor de donde se convoca el comando.
    """

    return archivos.cargar_pares_valores(PREFIXES_FILE).get(str(mensaje.guild.id), DEFAULT_PREFIX)


bot = commands.Bot(command_prefix=get_prefijo)

@bot.event
async def on_ready() -> None:
    """
    El bot se conectó y está listo para usarse.
    """

    print(f'[ {str(datetime.now())} ] ¡{bot.user} conectado y listo para utilizarse!')

@bot.event
async def on_guild_join(guild: Guild) -> None:
    """
    El bot se conectó por primera vez a un servidor.
    """

    print(f'[ {str(datetime.now())} ] El bot se conectó a "{guild.name}"')

    dic_prefijos = archivos.cargar_pares_valores(PREFIXES_FILE)
    dic_prefijos[str(guild.id)] = DEFAULT_PREFIX

    archivos.guardar_pares_valores(dic_prefijos, PREFIXES_FILE)

@bot.command(name='suma', aliases=['plus', '+'], help='suma dos enteros')
async def suma(ctx, num1: int, num2: int) -> None:
    """
    Suma dos enteros y envía por el canal el resultado.
    """

    await ctx.send(f'{num1} + {num2} = {num1 + num2}')

@bot.command(name='prefix', aliases=['prefijo', 'pfx', 'px'], help='Cambia el prefijo de los comandos.')
async def cambiar_prefijo(ctx: commands.Context, nuevo_prefijo: str) -> None:
    """
    Cambia el prefijo utilizado para convocar a los comandos, solamente del
    servidor de donde el comando fue escrito.

    Se da por hecho que el servidor ya está memorizado en el diccionario.
    """

    prefijo_viejo = ctx.prefix

    dic_prefijos = archivos.cargar_pares_valores(PREFIXES_FILE)
    dic_prefijos[str(ctx.guild.id)] = nuevo_prefijo
    archivos.guardar_pares_valores(dic_prefijos, PREFIXES_FILE)

    await ctx.channel.send(f'**[AVISO]** El prefijo de los comandos fue cambiado de `{prefijo_viejo}` a `{nuevo_prefijo}` exitosamente.', delete_after=30)
    