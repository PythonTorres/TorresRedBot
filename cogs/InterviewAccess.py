import discord
from discord.ext import commands
import settings

class InterviewAccess(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.text_channel = None
        self.voice_channel_id = settings.cogInterviewAccess['voiceChannel']
        self.text_channel_id = settings.cogInterviewAccess['textChannel']
        self.ignored_roles_ids = settings.cogInterviewAccess['ignoredRoles']

    @commands.Cog.listener()
    async def on_ready(self):
        print('[Cog: InterviewAccess] Cog is ready')
        self.text_channel = self.bot.get_channel(self.text_channel_id)
        if self.text_channel is not None:
            print(f'[Cog: InterviewAccess] Interview text channel ({self.text_channel.name}) found.')
        else:
            print('[Cog: InterviewAccess] Interview text channel was not found.')        

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):  

        if after.channel is not None and after.channel.id == self.voice_channel_id:  
            if (before.channel is not None and before.channel.id != self.voice_channel_id) or before.channel is None:
                for member_role in member.roles:
                    if member_role.id in self.ignored_roles_ids:
                        print(f'[Cog: InterviewAccess] Found ignored role ({member_role.name}) for {member.name}.')
                        return
                await self.text_channel.set_permissions(member, read_message_history = False, read_messages = True, send_messages = True)
                print(f'[Cog: InterviewAccess] Access granted for {member.name}.')
        
        if before.channel is not None and before.channel.id == self.voice_channel_id:
            if (after.channel is not None and after.channel.id != self.voice_channel_id) or after.channel is None:
                await self.text_channel.set_permissions(member, overwrite=None)
                print(f'[Cog: InterviewAccess] {member.name} disconnected from interview channel. Overwrites deleted.')


def setup(bot):
    bot.add_cog(InterviewAccess(bot))