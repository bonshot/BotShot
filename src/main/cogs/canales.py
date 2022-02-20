"""
Cog que agrupa comandos para los canales.
"""

from discord.ext.commands import Context, command, has_role

from ..archivos import cargar_json, guardar_json
from ..auxiliares import conseguir_id_canal
from ..constantes import DEV_ROLE_ID, PROPERTIES_FILE
from .categoria_comandos import CategoriaComandos


class CogCanales(CategoriaComandos):
    """
    Cog para los comandos que interactúan con
    información sobre los canales.
    """

    @command(name='listach',
             aliases=['lsch'],
             help='Mostrar lista de canales que el bot escucha')
    @has_role(DEV_ROLE_ID)
    async def mostrar_channels(self, ctx: Context) -> None:
        """
        Muestra en discord una lista de los canales que el bot está escuchando.
        """
        lista_id_canales = cargar_json(PROPERTIES_FILE).get('canales_escuchables')
        canales = []
        await ctx.message.delete(delay=10)
        for id_canal in lista_id_canales:
            canales.append(f'**{ctx.guild.get_channel(int(id_canal)).mention}**:\t`{id_canal}`')

        mensaje_canales = '>>> ' + '\n'.join(canales)
        await ctx.channel.send('**Lista de Canales Escuchando Actualmente:**\n\n' +
                               f'{mensaje_canales}',
                               delete_after=10)


    @command(name='agregarch',
             aliases=['addch'],
             help='Agregar canal al que el bot escucha (Mención al canal para uno en específico)')
    @has_role(DEV_ROLE_ID)
    async def agregar_channel(self, ctx: Context) -> None:
        """
        Agrega un nuevo canal para que escuche el bot.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        lista_canales = dic_propiedades['canales_escuchables']
        id_canal = conseguir_id_canal(ctx)
        await ctx.message.delete(delay=10)

        if str(id_canal) not in lista_canales:
            lista_canales += [str(id_canal)]
            dic_propiedades['canales_escuchables'] = lista_canales
            guardar_json(dic_propiedades, PROPERTIES_FILE)
            await ctx.channel.send(f'Canal `{ctx.guild.get_channel(id_canal).name}` ' +
                                    'guardado exitosamente en los escuchados!',
                                   delete_after=10)
        else:
            await ctx.channel.send(f'El canal `{ctx.guild.get_channel(id_canal).name}` ' +
                                    'ya está agregado, no lo voy a poner de nuevo, crack',
                                   delete_after=10)


    @command(name='eliminarch',
             aliases=['removech', 'delch'],
             help='Remover un canal al que el bot escucha ' +
                  '(Mención al canal para uno en específico)')
    @has_role(DEV_ROLE_ID)
    async def eliminar_channel(self, ctx: Context) -> None:
        """
        Elimina un canal existente en escucha del bot.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        lista_canales = dic_propiedades['canales_escuchables']
        id_canal = conseguir_id_canal(ctx)
        nombre_canal = ctx.guild.get_channel(id_canal).name
        await ctx.message.delete(delay=10)

        if str(id_canal) not in lista_canales:
            await ctx.channel.send(f'{ctx.author.mention}, papu, alma mía, corazon de mi vida, ' +
                                   f'el canal `{nombre_canal}` no está en la lista de canales ' +
                                    'a escuchar. No lo podés eliminar',
                                   delete_after=10)
        else:
            lista_canales.remove(str(id_canal))
            guardar_json(dic_propiedades, PROPERTIES_FILE)
            await ctx.channel.send(f'El canal `{nombre_canal}` fue eliminado exitosamente, pa',
                                   delete_after=10)
