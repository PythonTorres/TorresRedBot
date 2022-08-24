from datetime import time
from os import close
from discord import Embed, Colour
from discord.ext import commands, tasks
from discord.channel import DMChannel
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, component
from discord.errors import Forbidden, HTTPException
from discord.utils import get
import random
from datetime import datetime
import settings
from Database import Database

class Bets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dataBase = Database()
        self.discordComponents = DiscordComponents(bot)
        self.optionToEmoji = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣', 10: '🔟', 'default': '⏺'}
        self.aBetIsProcessing = False

    @tasks.loop(seconds = settings.cogBets['checkRegistrationAndNewTransactionsLoopTime'])
    async def checkRegistrationAndNewTransactions(self):
        createdAccounts = self.dataBase.compareRegAndTransactions(instantActions=True)
        if createdAccounts != False:
            await self.notifyUsersAboutSuccessfulReg(createdAccounts)
        balanceIncreases = self.dataBase.getNewTransactionsAndIncreaseBalances()
        if balanceIncreases != False:
            await self.notifyUsersAboutBalanceIncrease(balanceIncreases)

    @tasks.loop(seconds = settings.cogBets['checkWithdrawLoopTime'])
    async def checkWithdraw(self):
        withdrawUsers = self.dataBase.checkWithdraw()
        if withdrawUsers != False:
            for withdraw in withdrawUsers:
                user = await self.bot.fetch_user(withdraw['id'])
                try:
                    await user.send(settings.cogBets['withdrawSuccessMessageText'].format(withdraw['amount'], withdraw['account']))
                except Forbidden:
                    print('Could not DM withdraw user with id ' + str(withdraw['id']))

    #not tested the race condition proactive fix but should be okay
    @tasks.loop(seconds = settings.cogBets['checkForExpiredRegLoopTime'])
    async def checkRegistrationExpired(self):
        regsExpired = self.dataBase.checkRegsExpired()
        if regsExpired != False:
            recentlyCreated = self.dataBase.compareRegAndTransactions(instantActions=False)
            if recentlyCreated != False:
                recentlyCreatedIds = []
                for id in recentlyCreated:
                    recentlyCreatedIds.append(id['id'])
                compareResult = set(regsExpired) & set(recentlyCreatedIds)
                if len(compareResult) == 0:
                    print('regsExpired1')
                    for regForPrint in regsExpired: print(str(regForPrint)) #prints regs exp
                    self.dataBase.deleteRegsExpired(regsExpired)
                    await self.notifyUsersAboutExpiredReg(regsExpired)
                else:
                    restRegsExpired = regsExpired
                    for result in compareResult:
                        restRegsExpired = list(filter((result).__ne__, restRegsExpired))
                    if len(restRegsExpired) != 0:
                        print('restRegsExpired')
                        print(restRegsExpired)
                        self.dataBase.deleteRegsExpired(restRegsExpired)
                        await self.notifyUsersAboutExpiredReg(restRegsExpired)
            else:
                print('regsExpired2')
                for regForPrint in regsExpired: print(str(regForPrint)) #prints regs exp
                self.dataBase.deleteRegsExpired(regsExpired)
                await self.notifyUsersAboutExpiredReg(regsExpired)

    @tasks.loop(seconds = settings.cogBets['checkForExpiredWaitForBetLoopTime'])
    async def checkWaitForBetExpired(self):
        if self.aBetIsProcessing == False:
            waitForBetExpired = self.dataBase.checkWaitForBetExpired()
            if waitForBetExpired != False:
                self.dataBase.deleteWaitForBetExpired(waitForBetExpired)
                for betExpired in waitForBetExpired:
                    message = settings.cogBets['betExpiredMessageText']
                    toSend = await self.bot.fetch_user(betExpired)
                    try:
                        await toSend.send(message)
                    except Forbidden:
                        print('Could not DM a regExpired user with id = ' + str(betExpired))

    @tasks.loop(seconds = settings.cogBets['checkForCloseEventTime'])
    async def checkForCloseEvent(self):
        eventsToCloseIds = self.dataBase.getEventsToClose()
        for eventId in eventsToCloseIds:
            await self.closeEventByTime(eventId)

    @commands.Cog.listener()
    async def on_ready(self):
        print('[Cog: Bets] Cog is ready')
        if self.dataBase is not None:
            if settings.setEnviroment == 1:
                self.checkRegistrationAndNewTransactions.start()
                self.checkRegistrationExpired.start()
                self.checkWaitForBetExpired.start()
                self.checkWithdraw.start()
                self.checkForCloseEvent.start()
            print('[Cog: Bets] Database connection is established, tasks started')
        else:
            print('[Cog: Bets] Database connection failed')

    @commands.command()
    @commands.is_owner()
    async def registration(self, ctx):
        regChannel = self.bot.get_channel(settings.cogBets['registrationTextChannel'])
        await ctx.message.delete()
        try:
            messages = await regChannel.history(oldest_first = True).flatten() 
            prevRegMessage = messages[0]
            await prevRegMessage.delete()
        except IndexError:
            pass

        await regChannel.send(
            settings.cogBets['registrationText'],
            components = [Button(style=ButtonStyle.blue, label='Регистрация')]
        )

    @commands.command()
    async def createEvent(self, ctx, title, colour, thumbnail, closeWhen, *options):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        if closeWhen != '-':
            try:
                closeWhenTime = datetime.strptime(closeWhen, '%d.%m.%Y %H:%M')
            except ValueError:
                await ctx.author.send(settings.cogBets['eventCloseWhenCannotBeConvertedMessage'])
                return
        else:
            closeWhenTime = '-'

        embed = Embed(
            author = self.bot.user.name,
            title = title,
            colour = Colour(int(colour)),
            description = settings.cogBets['eventDescriptionText']
        )
        count = 0
        selectOptions = [SelectOption(label='Снять выделение', value=count, description='Сбрасывает выбранный исход', emoji='✖')]
        for field in options:
            count += 1
            eventOption = field
            eventValue = settings.cogBets['betFieldDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            eventOptionDescription = settings.cogBets['betOptionDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            embed.add_field(
                name = eventOption,
                value = eventValue,
                inline = False
            )
            if len(options) < 12:
                emoji = self.optionToEmoji[count]
            else:
                emoji = self.optionToEmoji['default']
            selectOptions.append(SelectOption(label=eventOption, value=count, description=eventOptionDescription, emoji=emoji))
        embed.set_footer(text = settings.cogBets['eventFooterText'].format(ctx.author.name), icon_url = ctx.author.avatar_url)
        if thumbnail != 'no':
            embed.set_thumbnail(url=thumbnail)
        eventMessage = await ctx.send(
            embed = embed,
            components = [Select(placeholder=settings.cogBets['eventSelectPlaceholderText'], options=selectOptions)]
        )
        self.dataBase.createEvent(eventMessage.id, eventMessage.channel.id, title, closeWhenTime)
        if closeWhen != '-':
            await ctx.author.send(settings.cogBets['eventCloseWhenSetDuringCreationMessage'].format(title, closeWhen))

    @commands.command()
    async def testEvent(self, ctx, title, colour, thumbnail, closeWhen, *options):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        if closeWhen != '-':
            try:
                closeWhenTime = datetime.strptime(closeWhen, '%d.%m.%Y %H:%M')
            except ValueError:
                await ctx.author.send(settings.cogBets['eventCloseWhenCannotBeConvertedMessage'])
                return
        else:
            closeWhenTime = '-'
        embed = Embed(
            author = self.bot.user.name,
            title = title,
            colour = Colour(int(colour)),
            description = settings.cogBets['eventDescriptionText']
        )
        count = 0
        selectOptions = [SelectOption(label='Снять выделение', value=count, description='Сбрасывает выбранный исход', emoji='✖')]
        for field in options:
            count += 1
            eventOption = field
            eventValue = settings.cogBets['betFieldDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            eventOptionDescription = settings.cogBets['betOptionDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            embed.add_field(
                name = eventOption,
                value = eventValue,
                inline = False
            )
            if len(options) < 10:
                emoji = self.optionToEmoji[count]
            else:
                emoji = self.optionToEmoji['default']
            selectOptions.append(SelectOption(label=eventOption, value=count, description=eventOptionDescription, emoji=emoji))
        embed.set_footer(text = settings.cogBets['eventFooterText'].format(ctx.author.name), icon_url = ctx.author.avatar_url)
        if thumbnail != 'no':
            embed.set_thumbnail(url=thumbnail)
        eventMessage = await ctx.send(
            embed = embed,
            components = [Select(placeholder=settings.cogBets['eventSelectPlaceholderText'], options=selectOptions)]
        )
        if closeWhen != '-':
            await ctx.send('Тестовое событие: ' + settings.cogBets['eventCloseWhenSetDuringCreationMessage'].format(title, closeWhen))

    @commands.command()
    async def closeEvent(self, ctx, eventId):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        id = int(eventId)
        event = self.dataBase.isEventActive(id)
        if event == False:
            await ctx.author.send(settings.cogBets['eventCannotCloseNotActiveEventMessageText'])
            return
        self.dataBase.closeEvent(id)
        await self.disableEventMessageSelector(ctx.channel.id, id)
        await ctx.author.send(settings.cogBets['eventEventHasBeenClosedMessageText'].format(event))

    @commands.command()
    async def openEvent(self, ctx, eventId):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        id = int(eventId)
        event = self.dataBase.isEventInactive(id)
        if event == False:
            await ctx.author.send(settings.cogBets['eventCannotOpenNotInactiveEventMessageText'])
            return
        self.dataBase.openEvent(id)
        await self.enableEventMessageSelector(ctx.channel.id, id)
        await ctx.author.send(settings.cogBets['eventEventHasBeenOpenedMessageText'].format(event))

    @commands.command()
    async def summarizeEvent(self, ctx, eventId):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        event = self.dataBase.isEventInactive(eventId) 
        if event == False:
            await ctx.author.send(settings.cogBets['eventCannotSummarizeNotInactiveMessageText'])
            return
        waitingBets = self.dataBase.getWaitingBetsNumberForEvent(eventId)
        if waitingBets != 0:
            await ctx.author.send(settings.cogBets['eventCannotSummarizeWaitingBetsMessageText'].format(waitingBets))
            return
        eventMessage = await ctx.channel.fetch_message(eventId)
        if eventMessage == None:
            await ctx.author.send(settings.cogBets['eventCannotSummarizeCannotFetchEventMessageText'])
            return
        eventForReview = await ctx.author.send(embed=eventMessage.embeds[0], components=eventMessage.components[0])
        self.dataBase.setEventInReview(eventId, eventForReview.id)
        await ctx.author.send(settings.cogBets['eventSummarizeChooseWinnerMessageText'])
        await self.enableEventMessageSelector(eventForReview.channel.id, eventForReview.id)

    @commands.command()
    async def withdraw(self, ctx, amount):
        if not isinstance(ctx.channel, DMChannel):
            return
        if self.dataBase.isUserAlreadyRegistered(ctx.author.id) == False:
            await ctx.send(settings.cogBets['withdrawNotRegisteredMessageText'])
            return
        userBalance = self.dataBase.getUserBalance(ctx.author.id)
        if userBalance == 0:
            await ctx.send(settings.cogBets['withdrawZeroBalanceMessageText'])
            return
        try:
            withdrawAmount = int(amount)
        except ValueError:
            await ctx.send(settings.cogBets['withdrawIncorrectAmountMessageText'])
            return
        if withdrawAmount <= 0:
            await ctx.send(settings.cogBets['withdrawNegativeAmountMessageText'])
            return
        if withdrawAmount > userBalance:
            await ctx.send(settings.cogBets['withdrawAmountGreaterThanBalanceMessageText'])
            return
        newWithdrawAmount = self.dataBase.createWithdraw(ctx.author.id, self.dataBase.getUserAccount(ctx.author.id), withdrawAmount)
        await ctx.send(settings.cogBets['withdrawCreatedMessageText'].format(newWithdrawAmount, self.dataBase.getUserBalance(ctx.author.id)))
    
    @commands.command()
    @commands.is_owner()
    async def withdrawList(self, ctx):
        await ctx.message.delete()
        withdrawList = self.dataBase.getWithdrawList()
        if withdrawList == False:
            await ctx.send(settings.cogBets['withdrawListNoItemsMessageText'])
            return
        withdrawListMessage = settings.cogBets['withdrawListStartText']
        for withdrawItem in withdrawList:
            withdrawItemText = settings.cogBets['withdrawListItemText'].format(withdrawItem['amount'], withdrawItem['account'], withdrawItem['name'])
            withdrawListMessage = withdrawListMessage + withdrawItemText
        await ctx.send(withdrawListMessage)

    @commands.command()
    async def addOptions(self, ctx, eventId, *options):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        eventChannel = await self.bot.fetch_channel(ctx.channel.id)
        eventMessage = await eventChannel.fetch_message(eventId)
        selectOptions = eventMessage.components[0][0].options
        embed = eventMessage.embeds[0]
        count = len(embed.fields)
        for field in options:
            count += 1
            eventOption = field
            eventValue = settings.cogBets['betFieldDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            eventOptionDescription = settings.cogBets['betOptionDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            embed.add_field(
                name = eventOption,
                value = eventValue,
                inline = False
            )
            if count < 12:
                emoji = self.optionToEmoji[count]
            else:
                emoji = self.optionToEmoji['default']
            selectOptions.append(SelectOption(label=eventOption, value=count, description=eventOptionDescription, emoji=emoji))
        await eventMessage.edit(
            embed = embed,
            components = [Select(placeholder=eventMessage.components[0][0].placeholder, options=selectOptions)]
        )
        
    @commands.command()
    async def editEventTitle(self, ctx, eventId, newEventTitle):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents'] or len(newEventTitle) == 0:
            return
        if not self.dataBase.isEventEditable(eventId):
            await ctx.author.send(settings.cogBets['eventEditImpossibleMessageText'].format(eventId))
            return
        eventChannel = await self.bot.fetch_channel(ctx.channel.id)
        eventMessage = await eventChannel.fetch_message(eventId)
        newEmbed = eventMessage.embeds[0]
        newEmbed.title = newEventTitle
        await eventMessage.edit(embed = newEmbed, components = eventMessage.components)
        self.dataBase.editEventTitle(eventId, newEventTitle)

    @commands.command()
    async def deleteEvent(self, ctx, eventId):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        if not self.dataBase.isEventEditable(eventId):
            await ctx.author.send(settings.cogBets['eventEditImpossibleMessageText'].format(eventId))
            return
        if self.dataBase.existingBetsForEvent(eventId):
            await ctx.author.send(settings.cogBets['eventDeleteImpossibleBetsExistMessageText'].format(eventId))
            return
        if self.dataBase.isEventInactive(eventId) == False:
            await ctx.author.send(settings.cogBets['eventDeleteImpossibleEventNotClosedMessageText'].format(eventId))
            return
        waitingBets = self.dataBase.getWaitingBetsNumberForEvent(eventId)
        if waitingBets != 0:
            await ctx.author.send(settings.cogBets['eventDeleteImpossibleBetsWaitingMessageText'].format(eventId, waitingBets))
            return
        self.dataBase.deleteEvent(eventId)
        eventChannel = await self.bot.fetch_channel(ctx.channel.id)
        eventMessage = await eventChannel.fetch_message(eventId)
        await eventMessage.delete()

    @commands.command()
    @commands.is_owner()
    async def rollbackEvent(self, ctx, eventId):
        await ctx.message.delete()
        if not self.dataBase.isEventEditable(eventId):
            await ctx.author.send(settings.cogBets['eventEditImpossibleMessageText'].format(eventId))
            return
        eventName = self.dataBase.isEventInactive(eventId)
        if eventName == False:
            await ctx.author.send(settings.cogBets['eventRollbackImpossibleEventNotClosedMessageText'].format(eventId))
            return
        waitingBets = self.dataBase.getWaitingBetsNumberForEvent(eventId)
        if waitingBets != 0:
            await ctx.author.send(settings.cogBets['eventRollbackImpossibleBetsWaitingMessageText'].format(eventId, waitingBets))
            return
        rollbackUsers = self.dataBase.rollbackEvent(eventId)
        rollbackMessage = settings.cogBets['eventRollbackMessageStartText'].format(eventId, eventName)
        for rollbackUser in rollbackUsers:
            userToNotify = await self.bot.fetch_user(rollbackUser['id'])
            userBalance = self.dataBase.getUserBalance(rollbackUser['id'])
            userName = self.dataBase.getUserName(rollbackUser['id'])
            rollbackMessage += settings.cogBets['eventRollbackMessagePieceText'].format(userName, rollbackUser['bet'])
            try:
                await userToNotify.send(settings.cogBets['betRollbackNotifyMessageText'].format(eventName, rollbackUser['bet'], userBalance))
            except Forbidden:
                print('Could not DM user with rollback. id = ' + rollbackUser['id'])
        await self.updateCoefsForEvent(eventId)
        await ctx.author.send(rollbackMessage)
    
    @commands.command()
    async def closeWhen(self, ctx, eventId, closeWhen):
        await ctx.message.delete()
        if ctx.author.id not in settings.cogBets['accessEvents']:
            return
        eventName = self.dataBase.getEventName(eventId)
        if eventName == False:
            await ctx.author.send(settings.cogBets['eventCloseWhenCannotBeSetAsEventNotFoundMessage'])
            return
        if self.dataBase.isEventActive(eventId) == False:
            await ctx.author.send(settings.cogBets['eventCloseWhenCannotBeSetAsEventIsNotActiveMessage'].format(eventName))
            return
        if closeWhen == '-':
            self.dataBase.setCloseWhenForEventToNull(eventId)
            await ctx.author.send(settings.cogBets['eventCloseWhenIsSetToNullMessage'].format(eventName))
            return
        try:
            closeWhenTime = datetime.strptime(closeWhen, '%d.%m.%Y %H:%M')
        except ValueError:
            await ctx.author.send(settings.cogBets['eventCloseWhenCannotBeConvertedMessage'])
            return
        self.dataBase.setCloseWhenForEvent(eventId, closeWhenTime)
        await ctx.author.send(settings.cogBets['eventCloseWhenIsSetMessage'].format(eventName, closeWhen))

    @commands.Cog.listener()
    async def on_button_click(self, res):
        eventToConfirm = self.dataBase.getSummarizedEventByConfirmationMessage(res.message.id)
        if eventToConfirm != False:
            await self.processConfirmation(res, eventToConfirm)
            return
        if res.channel.id == settings.cogBets['registrationTextChannel']:
            if self.dataBase.isUserAlreadyRegistered(res.author.id):
                await res.respond(
                    type=4,
                    content=settings.cogBets['registrationAlreadyRegisteredResponseText']
                )
                return
            if self.dataBase.getRegRecordForUser(res.author.id) != False:
                try:
                    message = settings.cogBets['registrationMessageRegReminderText'] + str(self.dataBase.getRegRecordForUser(res.author.id))
                    await res.author.send(message)
                    await res.respond(
                        type=4,
                        content=settings.cogBets['registrationAlreadyInProgressResponseText']
                    )
                except Forbidden:
                    await res.respond(
                        type=4,
                        content=settings.cogBets['registrationFailResponseText']
                    )
                return
            try:
                await self.startRegProcessForUser(res.author)
                await res.respond(
                    type=4,
                    content=settings.cogBets['registrationResponseText']
                )
            except Forbidden:
                await res.respond(
                    type=4,
                    content=settings.cogBets['registrationFailResponseText']
                )

    async def startRegProcessForUser(self, user):
        while True:
            regSum = random.randint(1000, 2000)
            if regSum not in self.dataBase.getRegistrationSums():
                break
        message = settings.cogBets['registrationMessageTextStart'] + str(regSum) + settings.cogBets['registrationMessageTextEnd']
        await user.send(message)
        fullUserName = user.name + '#' + user.discriminator
        self.dataBase.addNewRegRecord(user.id, fullUserName, regSum)

    async def notifyUsersAboutSuccessfulReg(self, accounts):
        betsGuild = self.bot.get_guild(settings.cogBets['betGuildId'])
        betsRole = get(betsGuild.roles, id=settings.cogBets['betsRoleId'])
        for user in accounts:
            message = settings.cogBets['registrationSuccessfulMessageText'].format(user['account'], user['amount'])
            sendTo = await self.bot.fetch_user(user['id'])
            member = await betsGuild.fetch_member(user['id'])
            await member.add_roles(betsRole)
            try:
                await sendTo.send(message)
            except Forbidden:
                print('Could not DM a registered user with id = ' + str(user['id']))

    async def notifyUsersAboutExpiredReg(self, regs):
        for user in regs:
            message = settings.cogBets['registrationExpiredMessageText']
            sendTo = await self.bot.fetch_user(user)
            try:
                await sendTo.send(message)
            except Forbidden:
                print('Could not DM a regExpired user with id = ' + str(user))

    async def notifyUsersAboutBalanceIncrease(self, increases):
        for user in increases:
            message = settings.cogBets['balanceIncreaseMessageText'].format(user['sum'], self.dataBase.getUserBalance(user['id']))
            sendTo = await self.bot.fetch_user(user['id'])
            try:
                await sendTo.send(message)
            except Forbidden:
                print('Could not DM an increasedBalance user with id = ' + str(user['id']))

    @commands.Cog.listener()
    async def on_select_option(self, click):
        if click.component[0].value == '0':
            if self.dataBase.getWaitForBetSum(click.author.id) != False:
                self.dataBase.deleteWaitForBetSum(click.author.id)
                await click.respond(
                    type=4,
                    content=settings.cogBets['betWaitForBetRemovedText']
                )
                return
            try:
                await click.respond()
            except HTTPException:
                pass
            return
        eventInReview = self.dataBase.getEventInReview(click.message.id, int(click.component[0].value))
        if eventInReview != False:
            await self.askToConfirm(click, eventInReview)
            return
        if self.dataBase.isUserAlreadyRegistered(click.author.id) == False:
            await click.respond(
                    type=4,
                    content=settings.cogBets['betUserNotRegisteredText']
                )
            return
        eventName = self.dataBase.isEventActive(click.message.id)
        if eventName == False:
            await click.respond(
                    type=4,
                    content=settings.cogBets['betEventNotFoundText']
                )
            return
        if self.dataBase.getWaitForBetSum(click.author.id) != False:
            await click.respond(
                    type=4,
                    content=settings.cogBets['betWaitForBetInProgressText']
                )
            return
        balance = self.dataBase.getUserBalance(click.author.id)
        message = settings.cogBets['betAskForBetText'].format(eventName, click.component[0].label, balance)
        try:
            await click.author.send(message)
        except Forbidden:
            await click.respond(
                    type=4,
                    content=settings.cogBets['betForbiddenErrorText']
                )
            print('Could not DM to ask for bet user ' + str(click.author.id))
            return
        self.dataBase.createWaitForBetSum(click.author.id, click.message.id, click.component[0].value)
        await click.respond(
                    type=4,
                    content=settings.cogBets['betEventCheckDMToConfirmText']
                )

    @commands.Cog.listener()
    async def on_message(self, message):
        if not isinstance(message.channel, DMChannel):
            return
        betToPlace = self.dataBase.getWaitForBetSum(message.author.id)
        if betToPlace == False:
            return
        try:
            betSum = int(message.content)
        except ValueError:
            await message.channel.send(settings.cogBets['betAskForCorrectValueText'])
            return
        if betSum < 0:
            await message.channel.send(settings.cogBets['betAskForPositiveValueText'])
            return
        if betSum == 0:
            self.dataBase.deleteWaitForBetSum(message.author.id)
            await message.channel.send(settings.cogBets['betWaitForBetCancelledText'])
            return
        if betSum > self.dataBase.getUserBalance(message.author.id):
            await message.channel.send(settings.cogBets['betBalanceLowerThanBetText'])
            return
        self.aBetIsProcessing = True
        await self.placeBetAndNotifyUser(betToPlace, betSum, message.channel)
        await self.updateCoefsForEvent(betToPlace['event_id'])

    async def placeBetAndNotifyUser(self, betToPlace, betSum, channelToAnswer):
        try:
            self.dataBase.placeBet(betToPlace['id'], betToPlace['event_id'], betToPlace['option_id'], betSum)
        except:
            await channelToAnswer.send(settings.cogBets['betDefaultExceptionMessageText'])
            return
        message = settings.cogBets['betSuccessMessageText'].format(betSum)
        await channelToAnswer.send(message)
        print(f"Bet by {betToPlace['id']}\nEvent {betToPlace['event_id']}\nOption {betToPlace['option_id']}\nSum {betSum}")
        self.aBetIsProcessing = False

    async def updateCoefsForEvent(self, eventId):
        newCoefs = self.dataBase.updateCoefsForEvent(eventId)
        eventChannelId = self.dataBase.getChannelIdForEvent(eventId)
        eventChannel = await self.bot.fetch_channel(eventChannelId)
        eventMessage = await eventChannel.fetch_message(eventId)
        if newCoefs == False:
            await self.resetCoefsForEventMessage(eventMessage)
            return
        newEmbed = eventMessage.embeds[0]
        for coef in newCoefs:
            newName = newEmbed.fields[coef['id']-1].name
            newValue = settings.cogBets['betFieldDescriptionText'].format(sum=coef['sum'],coef=coef['value'])
            newEmbed.set_field_at(index=coef['id']-1, name=newName, value=newValue, inline = False)
        count = 0
        newOptions = [eventMessage.components[count][count].options[count]]
        for field in newEmbed.fields:
            count += 1
            newLabel = eventMessage.components[0][0].options[count].label
            newValue = eventMessage.components[0][0].options[count].value
            newEmoji = eventMessage.components[0][0].options[count].emoji
            found = False
            for coef in newCoefs:
                if count == coef['id']:
                    newDescription = settings.cogBets['betOptionDescriptionText'].format(coef=coef['value'], sum=coef['sum'])
                    newOptions.append(SelectOption(label=newLabel, value=newValue, description=newDescription, emoji=newEmoji))
                    found = True
                    break
            if found is not True:
                newDescription = settings.cogBets['betOptionDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
                newOptions.append(SelectOption(label=newLabel, value=newValue, description=newDescription, emoji=newEmoji))
        newComponents = [Select(placeholder=eventMessage.components[0][0].placeholder, options=newOptions, disabled=eventMessage.components[0][0].disabled)]
        await eventMessage.edit(embed = newEmbed, components = newComponents)

    async def disableEventMessageSelector(self, channelId, messageId):
        channel = await self.bot.fetch_channel(channelId)
        message = await channel.fetch_message(messageId)
        newSelect = message.components[0][0]
        newSelect.disabled = True
        newSelect.placeholder = settings.cogBets['eventDisabledSelectPlaceholderText']
        await message.edit(embed = message.embeds[0], components = [newSelect])

    async def enableEventMessageSelector(self, channelId, messageId):
        channel = await self.bot.fetch_channel(channelId)
        message = await channel.fetch_message(messageId)
        newSelect = message.components[0][0]
        newSelect.disabled = False
        newSelect.placeholder = settings.cogBets['eventSelectPlaceholderText']
        await message.edit(embed = message.embeds[0], components = [newSelect])

    async def askToConfirm(self, click, eventInReview):
        content = settings.cogBets['eventSummarizeConfirmMessageText'].format(eventInReview['title'], click.component[0].label, eventInReview['sum'])
        components = [[Button(style=ButtonStyle.green, label='Подтвердить'), Button(style=ButtonStyle.red, label='Отмена')]]
        confirmationMessage = await click.author.send(content=content, components=components)
        self.dataBase.prepareEventConfirmation(eventInReview['id'], int(click.component[0].value), confirmationMessage.id)
        try:
            await click.respond()
        except HTTPException:
            pass

    async def processConfirmation(self, click, eventToConfirm):
        try:
            await click.respond()
        except HTTPException:
            pass
        if click.component.label == 'Отмена':
            self.dataBase.cancelConfirmation(eventToConfirm['id'])
            await click.author.send(settings.cogBets['eventSummarizeConfirmCanceledMessageText'])
            try:
                await click.respond()
            except HTTPException:
                pass
            return
        if click.component.label == 'Подтвердить':
            await click.author.send(settings.cogBets['eventSummarizeConfirmedMessageText'])
            isPay, result = self.dataBase.confirmEventSummarized(eventToConfirm['id'], eventToConfirm['winner'])
            eventChannelId = self.dataBase.getChannelIdForEvent(eventToConfirm['id'])
            eventChannel = await self.bot.fetch_channel(eventChannelId)
            eventMessage = await eventChannel.fetch_message(eventToConfirm['id'])
            if not isPay:
                for rollbackNotify in result:
                    userToNotify = await self.bot.fetch_user(rollbackNotify['id'])
                    eventName = self.dataBase.getEventName(eventToConfirm['id'])
                    userBalance = self.dataBase.getUserBalance(rollbackNotify['id'])
                    message = settings.cogBets['betRollbackNotifyMessageText'].format(eventName, rollbackNotify['bet'], userBalance)
                    try:
                        await userToNotify.send(message)
                    except Forbidden:
                        print('Could not DM a Rollbacked user with id ' + rollbackNotify['id'])
                await click.author.send(settings.cogBets['eventSummarizeConfirmRollbackMessageText'])
            elif isPay:
                winnersMessage = ''
                eventName = self.dataBase.getEventName(eventToConfirm['id'])
                winOption = eventMessage.embeds[0].fields[eventToConfirm['winner']-1].name
                for winNotify in result:
                    userToNotify = await self.bot.fetch_user(winNotify['id'])
                    userBalance = self.dataBase.getUserBalance(winNotify['id'])
                    message = settings.cogBets['betWinNotifyMessageText'].format(eventName, winOption, winNotify['win'], userBalance)
                    try:
                        await userToNotify.send(message)
                    except Forbidden:
                        print('Could not DM a Win user with id ' + winNotify['id'])
                    userName = self.dataBase.getUserName(winNotify['id'])
                    winnersMessage = winnersMessage + settings.cogBets['eventSummarizeWinnersPartText'].format(userName, winNotify['win'])
                winnersMessage = winnersMessage + settings.cogBets['eventSummarizeConfirmedAndPayedMessageText']
                await click.author.send(winnersMessage)
                print(winnersMessage)
            archivedEmbed = eventMessage.embeds[0]
            archivedEmbed.description = settings.cogBets['eventArchivedDescriptionText']
            newFieldName = eventMessage.embeds[0].fields[eventToConfirm['winner']-1].name + settings.cogBets['eventArchivedWinnerAddition']
            newFieldValue = eventMessage.embeds[0].fields[eventToConfirm['winner']-1].value
            archivedEmbed.set_field_at(index=eventToConfirm['winner']-1, name=newFieldName, value=newFieldValue, inline = False)
            archiveChannel = await self.bot.fetch_channel(settings.cogBets['archiveTextChannel'])
            await eventMessage.delete()
            archiveMessage = await archiveChannel.send(embed = archivedEmbed, components = [])
            self.dataBase.changeChannelAndMessageIdForArchivedEvent(eventToConfirm['id'], archiveMessage.id, archiveMessage.channel.id)

    async def resetCoefsForEventMessage(self, eventMessage):
        newEmbed = eventMessage.embeds[0]
        newOptions = [eventMessage.components[0][0].options[0]]
        count = 0
        for field in newEmbed.fields:
            newFieldValue = settings.cogBets['betFieldDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            newEmbed.set_field_at(index = count, name = field.name, value = newFieldValue, inline = False)
            newOptionLabel = eventMessage.components[0][0].options[count+1].label
            newOptionValue = eventMessage.components[0][0].options[count+1].value
            newOptionEmoji = eventMessage.components[0][0].options[count+1].emoji
            newOptionDesc = settings.cogBets['betOptionDescriptionText'].format(sum='0', coef=settings.cogBets['betFieldCoefDefaultText'])
            newOptions.append(SelectOption(label=newOptionLabel, value=newOptionValue, description=newOptionDesc, emoji=newOptionEmoji))
            count += 1
        newComponents = [Select(placeholder=eventMessage.components[0][0].placeholder, options=newOptions, disabled=eventMessage.components[0][0].disabled)]
        await eventMessage.edit(embed = newEmbed, components = newComponents)

    async def closeEventByTime(self, eventId):
        id = int(eventId)
        event = self.dataBase.isEventActive(id)
        if event == False:
            print('Could not close the event with id {} by time as it is not Active'.format(id))
            return
        self.dataBase.closeEvent(id)
        channelId = self.dataBase.getChannelIdForEvent(id)
        await self.disableEventMessageSelector(channelId, id)
        print('Event with id {} has been closed by time'.format(id))

    def cog_unload(self):
        print('[Cog: Bets] Cog unload is started')
        if settings.setEnviroment == 1:
            self.checkRegistrationAndNewTransactions.cancel()
            self.checkRegistrationExpired.cancel()
            self.checkWaitForBetExpired.cancel()
            self.checkWithdraw.cancel()
            self.checkForCloseEvent.cancel()
        self.dataBase.closeConnectionAndCursor()
        print('[Cog: Bets] Database connection is closed')
        return super().cog_unload()

def setup(bot):
    bot.add_cog(Bets(bot))