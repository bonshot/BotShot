"""
Módulo destinado a contener las funciones del bot.
"""
from discord import Guild, File
from discord.ext.commands import Context, has_role

import custom_bot
from custom_bot import log
import archivos
import os
import random

from constantes import DEV_ROLE_ID, PROPERTIES_FILE, IMAGES_PATH, DEFAULT_PREFIX


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

    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    dic_propiedades['prefijos'][str(guild.id)] = DEFAULT_PREFIX

    archivos.guardar_json(dic_propiedades, PROPERTIES_FILE)

@bot.command(name='suma', aliases=['plus', '+'], help='suma dos enteros')
async def suma(ctx, num1: int, num2: int) -> None:
    """
    Suma dos enteros y envía por el canal el resultado.
    """

    await ctx.send(f'{num1} + {num2} = {num1 + num2}')

@bot.command(name='prefix', aliases=['prefijo', 'pfx', 'px'], help='Cambia el prefijo de los comandos.')
async def cambiar_prefijo(ctx: Context, nuevo_prefijo: str) -> None:
    """
    Cambia el prefijo utilizado para convocar a los comandos, solamente del
    servidor de donde el comando fue escrito.

    Se da por hecho que el servidor ya está memorizado en el diccionario.
    """

    prefijo_viejo = ctx.prefix

    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    dic_propiedades['prefijos'][str(ctx.guild.id)] = nuevo_prefijo
    archivos.guardar_json(dic_propiedades, PROPERTIES_FILE)

    await ctx.channel.send(f'**[AVISO]** El prefijo de los comandos fue cambiado de `{prefijo_viejo}` a `{nuevo_prefijo}` exitosamente.', delete_after=30)

@bot.command(name='prueba', help='Esto es una prueba')
async def prueba(ctx: Context, *frase: str):
    """
    Esto es una prueba.
    """
    await ctx.channel.send(f'{ctx.author.mention} alias {ctx.author.name} con ID: {ctx.author.id}, Me dijiste: {" ".join(frase)}.', tts=True, mention_author=True)

def tiene_subcarpetas(path_dir: str) -> bool:
    """
    Verifica si una carpetas tiene carpetas hijas.
    """
    
    for elemento in os.listdir(path_dir):
        if os.path.isdir(os.path.join(path_dir, elemento)):
            return True

    return False

@bot.command(name='gimmeart', help='Manda una foto random')
async def gimmemoreart(ctx: Context) -> None:
    """
    Mandar una foto random
    """
    path_archivo = IMAGES_PATH

    while tiene_subcarpetas(path_archivo):
        path_archivo = os.path.join(path_archivo, random.choice(os.listdir(path_archivo)))
    foto_random = File(os.path.join(path_archivo, random.choice(os.listdir(path_archivo))))

    await ctx.channel.send(content=f"Disfruta de tu porno, puerco de mierda {ctx.author.mention}", file=foto_random)

def conseguir_id_canal(ctx: Context) -> int:
    """
    Si el mensaje tiene menciones a un canal, devuelve el id de la primera
    de esas menciones, caso contario devuelve el canal sobre el que está parado.
    """
    menciones_canales = ctx.message.channel_mentions

    if menciones_canales:
        return menciones_canales[0].id
    return ctx.channel.id

@bot.command(name='listach', aliases=['ch'], help='Mostrar lista de canales que el bot escucha')
@has_role(DEV_ROLE_ID)
async def mostrar_channels(ctx: Context) -> None:
    """
    Muestra en discord una lista de los canales que el bot está escuchando.
    """
    lista_id_canales = archivos.cargar_json(PROPERTIES_FILE).get('canales_escuchables')
    canales = []
    await ctx.message.delete(delay=10)
    for id_canal in lista_id_canales:
        canales.append(f"**{ctx.guild.get_channel(int(id_canal)).mention}**:\t`{id_canal}`")

    mensaje_canales = ">>> " + '\n'.join(canales)
    await ctx.channel.send(f"**Lista de Canales Escuchando Actualmente:**\n\n{mensaje_canales}", delete_after=10)

@bot.command(name='agregarch', aliases=['addch'], help='Agregar canal al que el bot escucha (Mención al canal para uno en específico)')
@has_role(DEV_ROLE_ID)
async def agregar_channel(ctx: Context) -> None:
    """
    Agrega un nuevo canal para que escuche el bot.
    """
    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    lista_canales = dic_propiedades["canales_escuchables"]
    id_canal = conseguir_id_canal(ctx)
    await ctx.message.delete(delay=10)
    
    if str(id_canal) not in lista_canales:
        lista_canales += [str(id_canal)]
        dic_propiedades["canales_escuchables"] = lista_canales
        archivos.guardar_json(dic_propiedades, PROPERTIES_FILE)
        await ctx.channel.send(f"Canal `{ctx.guild.get_channel(id_canal).name}` guardado exitosamente en los escuchados!", delete_after=10)
    else:
        await ctx.channel.send(f"El canal `{ctx.guild.get_channel(id_canal).name}` ya está agregado, no lo voy a poner de nuevo, crack", delete_after=10)

@bot.command(name='eliminarch', aliases=['removech'], help='Remover un canal al que el bot escucha (Mención al canal para uno en específico)')
@has_role(DEV_ROLE_ID)
async def eliminar_channel(ctx: Context) -> None:
    """
    Elimina un canal existente en escucha del bot.
    """
    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    lista_canales = dic_propiedades["canales_escuchables"]
    id_canal = conseguir_id_canal(ctx)
    nombre_canal = ctx.guild.get_channel(id_canal).name
    await ctx.message.delete(delay=10)

    if str(id_canal) not in lista_canales:
        await ctx.channel.send(f"{ctx.author.mention}, papu, alma mía, corazon de mi vida, el canal `{nombre_canal}` no está en la lista de canales a escuchar. No lo podés eliminar", delete_after=10)
    else:
        lista_canales.remove(str(id_canal))
        archivos.guardar_json(dic_propiedades, PROPERTIES_FILE)
        await ctx.channel.send(f"El canal `{nombre_canal}` fue eliminado exitosamente, pa", delete_after=10)


# @bot.command(name='download')
# async def descargar(ctx):
#     mensaje_referido = ctx.message.reference
#     if mensaje_referido and mensaje_referido:
#         mensaje_posta = await ctx.fetch_message(mensaje_referido.message_id)

#         if mensaje_posta.attachments:
#             imagen = mensaje_posta.attachments[0]
#             await imagen.save(f'{IMAGES_PATH}{imagen.filename}')

#             await ctx.channel.send("exito")