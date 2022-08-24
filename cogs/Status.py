import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup as BS

class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.servers = {'red': 0, 'green': 1, 'blue': 2, 'lime': 3}

    @commands.Cog.listener()
    async def on_ready(self):
        print('[Cog: Status] Cog is ready')
        self.status.start()
        if self.status.is_running():
            print('[Cog: Status] Status task is running')
        else:
            print('[Cog: Status] Status task is not running')

    
    @tasks.loop(seconds = 60)
    async def status(self):
        await self.bot.change_presence(activity = discord.Game('Red online: ' + self.get_online('red') + '/1000'))

    def cog_unload(self):
        print('[Cog: Status] Cog unload is started')
        self.status.cancel()

    def get_online(self, serverName):
        server_id = self.servers[serverName]
        ans = requests.get('https://www.advance-rp.ru/join/#')
        page = BS(ans.content, 'html.parser')
        result = page.select('.gamers > span[itemprop="playersOnline"]')
        return str(result[server_id].text)

    @commands.command()
    @commands.is_owner()
    async def status_update(self, ctx):
        await self.bot.change_presence(activity = discord.Game('Red online: ' + self.get_online('red') + '/1000'))
        await ctx.send('Bot status updated manually.')

    @commands.command()
    @commands.is_owner()
    async def status_stop(self, ctx):
        try:
            self.status.cancel()
            await ctx.send('Status task disabled.')
        except:
            await ctx.send('Status task is not launched.')

    @commands.command()
    @commands.is_owner()
    async def status_start(self, ctx):
        try:
            self.status.start()
            await ctx.send('Status task enabled.')
        except:
            await ctx.send('Status task is already launched.')
            

def setup(bot):
    bot.add_cog(Status(bot))