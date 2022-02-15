"""
Cog para comandos extras de usuarios.
"""

from discord.ext.commands import command, Context, has_role

from archivos import cargar_json, guardar_json
from categoria_comandos import CategoriaComandos
from constantes import PROPERTIES_FILE, DEV_ROLE_ID

class CogUsuarios(CategoriaComandos):
    """
    Cog para comandos de usuarios.
    """

    @command(name='recomendar', aliases=['recommend'], help='Recomienda una nueva carpeta')
    async def recomendar_carpeta(self, ctx: Context, nombre_carpeta: str):
        """
        Agrega un nombre de carpeta a los candidatos de nuevas
        carpetas a agregar.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        if nombre_carpeta not in dic_propiedades['carpetas_recomendadas']:
            dic_propiedades['carpetas_recomendadas'].append(nombre_carpeta)
            mensaje_a_mostrar = f"La carpeta {nombre_carpeta} fue recomendada rey!"
        else:
            mensaje_a_mostrar = "*Recomendado repetido pa*"
        guardar_json(dic_propiedades, PROPERTIES_FILE)

        await ctx.message.delete()
        await ctx.channel.send(mensaje_a_mostrar, delete_after=10)

    @command(name="recomendados", aliases=['recommended'], help='Muestra las carpetas recomendadas')
    @has_role(DEV_ROLE_ID)
    async def mostrar_recomendados(self, ctx: Context):
        """
        Muestra una lista de los nombres de carpetas que son candidatos
        a agregar.
        """
        dic_propiedades = cargar_json(PROPERTIES_FILE)
        recomendadas = dic_propiedades['carpetas_recomendadas']
        if recomendadas:
            mensaje_a_imprimir = ">>> \t**Lista de Recomendaciones:**\n\n" + '\n'.join(f'\t-\t`{nombre}`' for nombre in recomendadas)
        else:
            mensaje_a_imprimir = "*No hay recomendaciones crack*"

        await ctx.message.delete()
        await ctx.channel.send(content=mensaje_a_imprimir, delete_after=30)