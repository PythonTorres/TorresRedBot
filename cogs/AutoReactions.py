from discord.ext import commands
import settings

class AutoReactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.news_id = settings.cogAutoReactions['textChannel']

    @commands.Cog.listener()
    async def on_ready(self):
        print('[Cog: AutoReactions] Cog is ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.news_id:
            await message.add_reaction('👍')
            await message.add_reaction('👎')

def setup(bot):
    bot.add_cog(AutoReactions(bot))