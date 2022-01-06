"""
Módulo destinado a contener las funciones del bot.
"""
from discord import Guild, File, Message
from discord.ext.commands import Context, has_role

import custom_bot
from custom_bot import log
from interfaz import ConfirmacionGuardar
import archivos

from constantes import DEV_ROLE_ID, PROPERTIES_FILE, IMAGES_PATH, DEFAULT_PREFIX


bot = custom_bot.CustomBot()

def es_canal_escuchado(mensaje: Message):
    """
    Devuelve 'True' si se está en un canal escuchado.
    Si no, devuelve 'False'.
    """
    canal_actual = str(mensaje.channel.id)
    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    return canal_actual in dic_propiedades['canales_escuchables']

def mensaje_tiene_imagen(mensaje: Message):
    """
    Devuelve 'True' si el mensaje contiene una imagen.
    Caso contrario, devuelve 'False'.
    """
    if not mensaje.attachments: 
        return False

    for contenido in mensaje.attachments:
        if "image" not in contenido.content_type:
            return False

    return True

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

@bot.event
async def on_message(mensaje: Message):
    """
    Escucha un mensaje enviado si este tiene una imagen.
    """
    await bot.process_commands(mensaje)

    if any((mensaje.author == bot.user,
           not es_canal_escuchado(mensaje),
           not mensaje_tiene_imagen(mensaje))):
        return

    await mensaje.channel.send(content="¿Querés guardarlo pibe?", view=ConfirmacionGuardar(), delete_after=120, reference=mensaje.to_reference())

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

@bot.command(name='gimmeart', help='Manda una foto random')
async def gimmemoreart(ctx: Context) -> None:
    """
    Mandar una foto random
    """
    path_archivo = IMAGES_PATH

    while archivos.tiene_subcarpetas(path_archivo):
        path_archivo = archivos.carpeta_random(path_archivo)
    foto_random = File(archivos.archivo_random(path_archivo))

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

@bot.command(name='recomendar', aliases=['recommend'], help='Recomienda una nueva carpeta')
async def recomendar_carpeta(ctx: Context, nombre_carpeta: str):
    """
    Agrega un nombre de carpeta a los candidatos de nuevas
    carpetas a agregar.
    """
    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    if nombre_carpeta not in dic_propiedades['carpetas_recomendadas']:
        dic_propiedades['carpetas_recomendadas'].append(nombre_carpeta)
        mensaje_a_mostrar = f"La carpeta {nombre_carpeta} fue recomendada rey!"
    else:
        mensaje_a_mostrar = "*Recomendado repetido pa*"
    archivos.guardar_json(dic_propiedades, PROPERTIES_FILE)

    await ctx.message.delete()
    await ctx.channel.send(mensaje_a_mostrar, delete_after=10)

@bot.command(name="recomendados", aliases=['recommended'], help='Muestra las carpetas recomendadas')
@has_role(DEV_ROLE_ID)
async def mostrar_recomendados(ctx: Context):
    """
    Muestra una lista de los nombres de carpetas que son candidatos
    a agregar.
    """
    dic_propiedades = archivos.cargar_json(PROPERTIES_FILE)
    recomendadas = dic_propiedades['carpetas_recomendadas']
    if recomendadas:
        mensaje_a_imprimir = ">>> \t**Lista de Recomendaciones:**\n\n" + '\n'.join(f'\t-\t`{nombre}`' for nombre in recomendadas)
    else:
        mensaje_a_imprimir = "*No hay recomendaciones crack*"
    
    await ctx.message.delete()
    await ctx.channel.send(content=f"{mensaje_a_imprimir}", delete_after=30)