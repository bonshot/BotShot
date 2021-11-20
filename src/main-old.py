from asyncio import tasks
import discord
import os
from discord import channel
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import time
import os
import random
import sched

load_dotenv()
TOKEN = os.getenv('TOKEN')

#Prefijo del bot
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print('I have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name="Being Part of RGBT Community"))

@bot.event
async def on_message(message):
    if message.content.startswith('!hola'):
        await message.channel.send('Hola')
    await bot.process_commands(message)

@bot.event
async def on_message(message):
    if message.content.startswith('!test'):
        await message.channel.send("This test works fine")
    await bot.process_commands(message)

#Plus function
@bot.command(name = 'suma')
async def suma(ctx, num1, num2):
    response = int(num1) + int(num2)
    print(response)
    await ctx.send(response)



@bot.command(name='camioncito')
async def camioncito(ctx):
    '''Te pone un sonido random de un camioncito verdulero, jaja re piola'''
    sonido = random.choice([x for x in os.listdir("C:/Users/facu_/OneDrive/Escritorio/Proyectos  y programación/BotShot/bot-env-voice/bot-env/Sounds/camioncitos") if os.path.isfile(os.path.join("C:/Users/facu_/OneDrive/Escritorio/Proyectos  y programación/BotShot/bot-env-voice/bot-env/Sounds/camioncitos", x))])
    print(sonido)
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    audio_source = discord.FFmpegPCMAudio(executable="C:/Users/facu_/Downloads/ffmpeg/bin/ffmpeg.exe",source=f'Sounds/camioncitos/{sonido}')
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)

@bot.command(name='play_wawas')
async def play_wawas(ctx):
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    audio_source = discord.FFmpegPCMAudio(executable="C:/Users/facu_/Downloads/ffmpeg/bin/ffmpeg.exe",source='Sounds/hay_wa.mp3')
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)

#Checkear las y media para las waifus
async def time_check():
    await bot.wait_until_ready()
    while not bot.is_closed:
        channel = bot.get_channel(821736292030087178)
        f = '%M'
        now = datetime.strftime(datetime.now(), f)
        diff = (datetime.strptime(30, f) - datetime.strptime(now, f)).total_seconds()
        s = sched.scheduler(time.perf_counter, time.sleep)
        args = (play_wawas, )
        s.enter(1, bot.loop.create_task, args)
        s.run() 


bot.loop.create_task(time_check())

# Join command, joins the voice channel of whoever sent the command
@bot.command(name='entra')
@commands.has_permissions(administrator=True)
async def join(context):
    channel = context.author.voice.channel
    await channel.connect()

# Leave command, leaves the voice channel
@bot.command(name='tomatelas')
@commands.has_permissions(administrator=True)
async def leave(context):
    await context.voice_client.disconnect()

@bot.command(name = 'clear')
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=800):
	await ctx.channel.purge(limit=amount)

@bot.command(name='reload')
@commands.has_permissions(administrator=True)
async def rebootear_funciones(ctx):
    bot.reload_extension('main-old.py')

@bot.command(name='quit')
@commands.has_permissions(administrator=True)
async def close(ctx):
    await bot.logout()
    print("Bot Closed")

bot.run(TOKEN)
