from discord.ext import commands
from discord import DMChannel, HTTPException
from discord_components import DiscordComponents, Button, ButtonStyle
import settings
from Database import Database

class AttachmentApprove(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dataBase = Database()
        self.userTimers = [] #TODO add a cooldown and a queue for approved attachments

    @commands.Cog.listener()
    async def on_ready(self):
        print('[Cog: AttachmentApprove] Cog is ready')
        self.channel = await self.bot.fetch_channel(settings.cogAttachmentApprove['textChannel'])
        if self.channel is not None:
            print('[Cog: AttachmentApprove] Text channel fetched: ' + self.channel.name)
        else:
            print('[Cog: AttachmentApprove] Text channel not found.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not isinstance(message.channel, DMChannel):
            return
        attachments = message.attachments
        if len(attachments) == 0:
            return
        user = message.author
        
        for attachment in attachments:
            await self.sendAttachmentForApprove(user, attachment, self.channel)

    @commands.Cog.listener()
    async def on_button_click(self, click):
        if click.channel.id != settings.cogAttachmentApprove['textChannel']:
            await self.nullResponse(click)
            return
        if click.component.label == 'Приемлемо':
            outChannel = await self.bot.fetch_channel(settings.cogAttachmentApprove['outChannel'])
            userMention = self.dataBase.getUserMentionByApproveId(click.message.id)
            if userMention == False:
                await self.nullResponse(click)
                return
            content = settings.cogAttachmentApprove['messageWhenApproved'].format(userMention=userMention)
            file = await click.message.attachments[0].to_file()
            await outChannel.send(content=content, file=file)
            message = click.message
            newContent = message.content + '\n' + click.author.mention + ': приемлемо.'
            await message.edit(content=newContent, components=[])
            self.dataBase.deleteAttachmentForApprove(message.id)
            await self.nullResponse(click)
        elif click.component.label == 'Не приемлемо':
            message = click.message
            newContent = message.content + '\n' + click.author.mention + ': не приемлемо.'
            await message.edit(content=newContent, components=[])
            self.dataBase.deleteAttachmentForApprove(message.id)
            await self.nullResponse(click)
        else:
            print('[Cog: AttachmentApprove] ERROR: Button label not recognized')


    async def sendAttachmentForApprove(self, user, attachment, channel):
        content = settings.cogAttachmentApprove['messageWhenSentForApprove'].format(userMention=user.mention)
        components = [[Button(label='Приемлемо', style=ButtonStyle.green), Button(label='Не приемлемо', style=ButtonStyle.red)]]
        file = await attachment.to_file()
        sentMessage = await channel.send(content=content, file=file, components=components)
        self.dataBase.addAttachmentForApprove(sentMessage.id, user.mention, user.name)

    async def nullResponse(self, click):
        try:
            await click.respond()
        except HTTPException:
            pass

    def cog_unload(self):
        print('[Cog: AttachmentApprove] Cog unload is started')

def setup(bot):
    bot.add_cog(AttachmentApprove(bot))