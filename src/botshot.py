"""
Módulo destinado a contener las funciones del bot.
"""
from discord import Message, Guild, File
from discord.ext import commands
from datetime import datetime

import custom_bot
from custom_bot import log
import archivos
import os
import random

from constantes import PREFIXES_FILE, DEFAULT_PREFIX


PATH_CARPETA_SOSPECHOSA = 'D:\Carpeta para nada sospechosa\Fotos discord\\'
PATH_CARPETA_GUARDADO = 'C:/Users/facu_/OneDrive/Escritorio/Guardados/'


bot = custom_bot.CustomBot()

@bot.event
async def on_ready() -> None:
    """
    El bot se conectó y está listo para usarse.
    """

    log.info(f'¡{bot.user} conectado y listo para utilizarse!')

@bot.event
async def on_guild_join(guild: Guild) -> None:
    """
    El bot se conectó por primera vez a un servidor.
    """

    log.info(f'El bot se conectó a "{guild.name}"')

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

@bot.command(name='prueba', help='Esto es una prueba')
async def prueba(ctx, *frase: str):
    """
    Esto es una prueba.
    """
    await ctx.channel.send(f'{ctx.author.mention} alias {ctx.author.name} con ID: {ctx.author.id}, Me dijiste: {" ".join(frase)}.', tts=True, mention_author=True)

@bot.command(name='gimmeart', help='Prueba de foto random')
async def gimmemoreart(ctx):
    """
    Prueba de mandar una foto random
    """
    carpeta_random_path = random.choice(os.listdir(f"{PATH_CARPETA_SOSPECHOSA}"))
    foto_random_path = random.choice(os.listdir(f"{PATH_CARPETA_SOSPECHOSA}{carpeta_random_path}"))
    foto_random = File(f'{PATH_CARPETA_SOSPECHOSA}{carpeta_random_path}\{foto_random_path}')

    await ctx.channel.send(content=f"Disfruta de tu porno, puerco de mierda {ctx.author.mention}", file=foto_random)


@bot.command(name='download')
async def descargar(ctx):
    mensaje_referido = ctx.message.reference
    if mensaje_referido and mensaje_referido:
        mensaje_posta = await ctx.fetch_message(mensaje_referido.message_id)

        if mensaje_posta.attachments:
            imagen = mensaje_posta.attachments[0]
            await imagen.save(f'{PATH_CARPETA_GUARDADO}{imagen.filename}')

            await ctx.channel.send("exito")