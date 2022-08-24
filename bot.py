from discord.ext import commands
import os
import sys
import settings

bot = commands.Bot(command_prefix=settings.bot['prefix'], owner_id = settings.bot['owner'])

@bot.event
async def on_ready():
    print("Bot is online")

@bot.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.bot.close()

@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(settings.bot['token'])