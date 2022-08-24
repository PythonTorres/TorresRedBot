import psycopg2
import datetime
import math
import settings

class Database:

    def __init__(self):
        databaseURL = settings.cogBets['dataBaseURL']
        isConnectionEstablished = False #not really tested
        while isConnectionEstablished is False:
            print('[DATABASE] Establishing connection')
            try:
                self.connection = psycopg2.connect(databaseURL)
                self.cursor = self.connection.cursor()
                isConnectionEstablished = True
                print('[DATABASE] Connection established')
            except psycopg2.OperationalError:
                isConnectionEstablished = False
                print('[DATABASE] Connection failed, retrying...')

    def closeConnectionAndCursor(self):
        self.cursor.close()
        self.connection.close()

    def getAllTransactions(self):
        self.cursor.execute('select * from transactions')
        rows = self.cursor.fetchall()

        transactions = []
        for r in rows:
            transaction = {}
            transaction['id'] = r[0]
            transaction['date'] = r[1]
            transaction['amount'] = r[2]
            transaction['account'] = r[3]
            transaction['status'] = r[4]
            transactions.append(transaction)

        return transactions

    def addNewTransaction(self, transaction):
        self.cursor.execute("insert into transactions (id, date, amount, account, status) values (%s,%s,%s,%s,'New')", (transaction['id'], transaction['date'], transaction['amount'], transaction['account']))
        self.connection.commit()

    def getNumberOfTransactions(self):
        self.cursor.execute("select count(*) from transactions")
        return int(str(self.cursor.fetchall()[0])[1:-2])

    def isUserAlreadyRegistered(self, userDiscordId):
        self.cursor.execute("select id from users where id = " + str(userDiscordId))
        row = self.cursor.fetchall()
        if len(row) != 0:
            return True
        else:
            return False

    def getRegistrationSums(self):
        self.cursor.execute("select amount from registration")
        rows = self.cursor.fetchall()
        sums = []
        for row in rows:
            sums.append(row[0])
        return sums

    def addNewRegRecord(self, userDiscordId, userName, amount):
        self.cursor.execute("insert into registration (id, name, amount, created_when) values (%s, %s, %s, %s)", (userDiscordId, userName, amount, datetime.datetime.utcnow()))
        self.connection.commit()

    def getRegRecordForUser(self, userDiscordId):
        self.cursor.execute("select amount from registration where id = %s", (userDiscordId,))
        row = self.cursor.fetchall()
        if len(row) != 0:
            return row[0][0]
        else:
            return False

    def compareRegAndTransactions(self, instantActions):
        self.cursor.execute("select r.id, r.name, t.id, t.amount, t.account from registration r, transactions t where t.status = 'New' and r.amount = t.amount and t.amount > 0")
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        createdAccounts = []
        for row in rows:
            if not self.isUserAlreadyRegistered(row[0]):
                if instantActions == True:
                    self.cursor.execute("insert into users (id, name, balance, account, role) values (%s, %s, %s, %s, 'User')", (row[0], row[1], row[3], row[4]))
                    self.cursor.execute("update transactions set status = 'Old' where id = %s and amount > 0", (row[2],))
                    self.cursor.execute("delete from registration where id = %s", (row[0],))
                createdAccount = {}
                createdAccount['id'] = row[0]
                createdAccount['amount'] = row[3]
                createdAccount['account'] = row[4]
                createdAccounts.append(createdAccount)
                self.connection.commit()
        return createdAccounts

    def checkRegsExpired(self):
        expiredDateTime = datetime.datetime.utcnow() - datetime.timedelta(minutes=settings.cogBets['RegsAreExpiredAfterMinutes'])
        self.cursor.execute("select id from registration where created_when < %s", (expiredDateTime,))
        rows = self.cursor.fetchall()
        regsExpired = []
        if len(rows) == 0:
            return False
        for row in rows:
            regsExpired.append(row[0])
        return regsExpired

    def deleteRegsExpired(self, regs):
        for reg in regs:
            self.cursor.execute("delete from registration where id = %s", (reg,))
        self.connection.commit()

    def getNewTransactionsAndIncreaseBalances(self):
        self.cursor.execute("select u.id, sum(t.amount) from transactions t, users u where t.account = u.account and t.status = 'New' and t.amount > 0 group by u.id")
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        balanceIncreases = []
        for row in rows:
            balanceIncrease = {}
            balanceIncrease['id'] = row[0]
            balanceIncrease['sum'] = row[1]
            balanceIncreases.append(balanceIncrease)
            self.cursor.execute("update users set balance = balance + %s where id = %s", (row[1], row[0]))
        self.cursor.execute("update transactions set status = 'Old' where id in (select t.id from transactions t, users u where t.account = u.account and t.status = 'New') and amount > %s", (0,))
        self.connection.commit()
        return balanceIncreases

    def getUserBalance(self, userDiscordId):
        self.cursor.execute("select balance from users where id = %s", (userDiscordId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            print('Getting balance for user ' + userDiscordId + 'failed. No such user id in users table')
            return False
        return row[0][0]

    def createEvent(self, messageId, channelId, title, closeWhenTime):
        self.cursor.execute("insert into events (id, channel_id, title, status) values (%s, %s, %s, 'Active')", (messageId, channelId, title))
        self.connection.commit()
        if closeWhenTime != '-':
            self.setCloseWhenForEvent(messageId, closeWhenTime)
        else:
            self.setCloseWhenForEventToNull(messageId)

    def isEventActive(self, messageId):
        self.cursor.execute("select title from events where id = %s and status = 'Active'", (messageId,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
           return False
        else:
            return rows[0][0]

    def createWaitForBetSum(self, userDiscordId, eventId, optionId):
        self.cursor.execute("insert into wait_for_bet_sum (id, event_id, option_id, created_when) values (%s, %s, %s, %s)", (userDiscordId, eventId, optionId, datetime.datetime.utcnow()))
        self.connection.commit()

    def getWaitForBetSum(self, userDiscordId):
        self.cursor.execute("select * from wait_for_bet_sum where id = %s", (userDiscordId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        else:
            return {'id': row[0][0], 'event_id': row[0][1], 'option_id': row[0][2]}

    def deleteWaitForBetSum(self, userDiscordId):
        self.cursor.execute("delete from wait_for_bet_sum where id = %s", (userDiscordId,))
        self.connection.commit()

    def placeBet(self, userDiscordId, eventId, optionId, betSum):
        self.cursor.execute("update users set balance = balance - %s where id = %s", (betSum, userDiscordId))
        self.cursor.execute("delete from wait_for_bet_sum where id = %s", (userDiscordId,))
        self.cursor.execute("select id, bet from bets where user_id = %s and event_id = %s and option_id = %s", (userDiscordId, eventId, optionId))
        row = self.cursor.fetchall()
        if len(row) == 0:
            self.cursor.execute("insert into bets (user_id, event_id, option_id, bet) values (%s, %s, %s, %s)",(userDiscordId, eventId, optionId, betSum))
        else:
            self.cursor.execute("update bets set bet = bet + %s where id = %s", (betSum, row[0][0]))
        self.connection.commit()
    
    def checkWaitForBetExpired(self):
        expiredDateTime = datetime.datetime.utcnow() - datetime.timedelta(minutes=settings.cogBets['WaitForBetExpiredAfterMinutes'])
        self.cursor.execute("select id from wait_for_bet_sum where created_when < %s", (expiredDateTime,))
        rows = self.cursor.fetchall()
        waitForBetExpired = []
        if len(rows) == 0:
            return False
        for row in rows:
            waitForBetExpired.append(row[0])
        return waitForBetExpired

    def deleteWaitForBetExpired(self, bets):
        for bet in bets:
            self.cursor.execute("delete from wait_for_bet_sum where id = %s", (bet,))
        self.connection.commit()

    def updateCoefsForEvent(self, eventId):
        self.cursor.execute("select option_id, sum(bet) from bets where event_id = %s group by option_id", (eventId,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        newCoefs = []
        for row in rows:
            newCoef = {}
            newCoef['id'] = row[0]
            newCoef['sum'] = row[1]
            if len(rows) == 1:
                newCoef['value'] = settings.cogBets['betFieldCoefDefaultText']
                newCoefs.append(newCoef)
                return newCoefs
            sumOfOtherCoefs = 0
            for otherRow in list(filter((row).__ne__, rows)):
                sumOfOtherCoefs += otherRow[1]
            newCoefValue = sumOfOtherCoefs / row[1] + 1
            newCoef['value'] = int(newCoefValue*100)/100
            newCoefs.append(newCoef)
        return newCoefs

    def getChannelIdForEvent(self, eventId):
        self.cursor.execute("select channel_id from events where id = %s", (eventId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        return row[0][0]

    def closeEvent(self, eventId):
        self.cursor.execute("update events set status = 'Inactive' where id = %s", (eventId,))
        self.connection.commit()

    def isEventInactive(self, eventId):
        self.cursor.execute("select title from events where id = %s and status = 'Inactive'", (eventId,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
           return False
        else:
            return rows[0][0]

    def openEvent(self, eventId):
        self.cursor.execute("update events set status = 'Active' where id = %s", (eventId,))
        self.connection.commit()

    def getWaitingBetsNumberForEvent(self, eventId):
        self.cursor.execute("select count(id) from wait_for_bet_sum where event_id = %s group by event_id", (eventId,))
        rows = self.cursor.fetchall()
        return len(rows)

    def setEventInReview(self, eventId, eventReviewId):
        self.cursor.execute("update events set status = 'In Review' where id = %s", (eventId,))
        self.cursor.execute("insert into events_review (id, review_id) values (%s, %s)", (eventId, eventReviewId))
        self.connection.commit()

    def getEventInReview(self, eventReviewId, winnerOptionId):
        self.cursor.execute("select e.title, e.id from events_review er, events e, bets b where er.review_id = %s and er.id = e.id and e.status = 'In Review'", (eventReviewId,))
        rowInReview = self.cursor.fetchall()
        if len(rowInReview) == 0:
            return False
        self.cursor.execute("select e.title, e.id, sum(b.bet) from events_review er, events e, bets b where er.review_id = %s and er.id = e.id and e.id = b.event_id and b.option_id = %s group by e.title, e.id", (eventReviewId, winnerOptionId))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return {'title': rowInReview[0][0], 'id': rowInReview[0][1], 'sum': 0}
        return {'title': row[0][0], 'id': row[0][1], 'sum': row[0][2]}

    def prepareEventConfirmation(self, eventId, optionId, messageId):
        self.cursor.execute("update events_review set confirm_id = %s, winner = %s where id = %s", (messageId, optionId, eventId))
        self.connection.commit()

    def getSummarizedEventByConfirmationMessage(self, confirmId):
        self.cursor.execute("select id, winner from events_review where confirm_id = %s", (confirmId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        return {'id': row[0][0], 'winner': row[0][1]}

    def cancelConfirmation(self, eventId):
        self.cursor.execute("delete from events_review where id = %s", (eventId,))
        self.cursor.execute("update events set status = 'Inactive' where id = %s", (eventId,))
        self.connection.commit()

    def confirmEventSummarized(self, eventId, winnerId):
        self.cursor.execute("select option_id from bets where event_id = %s group by option_id", (eventId,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            self.cursor.execute("delete from events_review where id = %s", (eventId,))
            self.cursor.execute("update events set status = 'Archived' where id = %s", (eventId,))
            self.connection.commit()
            return False, []
        if len(rows) == 1:
            self.cursor.execute("select user_id, sum(bet) from bets where event_id = %s and option_id = %s group by user_id, option_id", (eventId, rows[0][0]))
            oneOptionBetRollback = self.cursor.fetchall()
            usersOneOptionRollback = []
            for userTotalBets in oneOptionBetRollback:
                self.cursor.execute("update users set balance = balance + %s where id = %s", (userTotalBets[1], userTotalBets[0]))
                self.cursor.execute("delete from events_review where id = %s", (eventId,))
                self.cursor.execute("update events set status = 'Archived' where id = %s", (eventId,))
                userOneOptionRollback = {}
                userOneOptionRollback['id'] = userTotalBets[0]
                userOneOptionRollback['bet'] = userTotalBets[1]
                usersOneOptionRollback.append(userOneOptionRollback)
            self.connection.commit()
            return False, usersOneOptionRollback
        self.cursor.execute("select user_id, sum(bet) from bets where event_id = %s and option_id = %s group by user_id", (eventId, winnerId))
        winnerUsersRows = self.cursor.fetchall()
        if len(winnerUsersRows) == 0:
            self.cursor.execute("select user_id, sum(bet) from bets where event_id = %s group by user_id", (eventId,))
            noWinnerBetsRollback = self.cursor.fetchall()
            usersOneOptionRollback = []
            for userTotalBets in noWinnerBetsRollback:
                self.cursor.execute("update users set balance = balance + %s where id = %s", (userTotalBets[1], userTotalBets[0]))
                self.cursor.execute("delete from events_review where id = %s", (eventId,))
                self.cursor.execute("update events set status = 'Archived' where id = %s", (eventId,))
                userOneOptionRollback = {}
                userOneOptionRollback['id'] = userTotalBets[0]
                userOneOptionRollback['bet'] = userTotalBets[1]
                usersOneOptionRollback.append(userOneOptionRollback)
            self.connection.commit()
            return False, usersOneOptionRollback
        #main logic
        self.cursor.execute("select sum(bet) from bets where event_id = %s and option_id = %s group by option_id", (eventId, winnerId))
        sumOfWinnerOptionBets = self.cursor.fetchall()
        self.cursor.execute("select sum(bet) from bets where event_id = %s and option_id <> %s group by event_id", (eventId, winnerId))
        sumOfOtherOptionsBets = self.cursor.fetchall()
        winnerCoefRaw = sumOfOtherOptionsBets[0][0] / sumOfWinnerOptionBets[0][0] + 1
        winnerCoef = int(winnerCoefRaw*100)/100
        winners = []
        for winnerUser in winnerUsersRows:
            winnerPlusSum = math.floor(winnerUser[1] * winnerCoef)
            self.cursor.execute("update users set balance = balance + %s where id = %s", (winnerPlusSum, winnerUser[0]))
            winner = {}
            winner['id'] = winnerUser[0]
            winner['win'] = winnerPlusSum
            winners.append(winner)
        self.cursor.execute("delete from events_review where id = %s", (eventId,))
        self.cursor.execute("update events set status = 'Archived' where id = %s", (eventId,))
        self.connection.commit()
        return True, winners

    def getEventName(self, eventId):
        self.cursor.execute("select title from events where id = %s", (eventId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        return row[0][0]
        
    def getUserName(self, userId):
        self.cursor.execute("select name from users where id = %s", (userId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        return row[0][0]

    def changeChannelAndMessageIdForArchivedEvent(self, eventId, newEventId, newEventChannelId):
        self.cursor.execute("update events set id = %s, channel_id = %s where id = %s", (newEventId, newEventChannelId, eventId))
        self.cursor.execute("update bets set event_id = %s where event_id = %s", (newEventId, eventId))
        self.connection.commit()

    def getUserAccount(self, userDiscordId):
        self.cursor.execute("select account from users where id = %s", (userDiscordId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            print('Getting account for user ' + userDiscordId + 'failed. No such user id in users table')
            return False
        return row[0][0]

    def createWithdraw(self, userDiscordId, userAccount, withdrawAmount):
        self.cursor.execute("select amount from withdraw where id = %s", (userDiscordId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            self.cursor.execute("insert into withdraw (id, account, amount) values (%s, %s, %s)", (userDiscordId, userAccount, withdrawAmount))
            newWithdrawAmount = withdrawAmount
        else:
            self.cursor.execute("update withdraw set amount = amount + %s where id = %s", (withdrawAmount, userDiscordId))
            newWithdrawAmount = row[0][0] + withdrawAmount
        self.cursor.execute("update users set balance = balance - %s where id = %s", (withdrawAmount, userDiscordId))
        self.connection.commit()
        return newWithdrawAmount

    def checkWithdraw(self):
        self.cursor.execute("select u.id, t.account, w.amount from withdraw w, transactions t, users u where w.account = t.account and t.status = 'New' and t.amount < 0 and t.account = u.account group by t.account, w.amount, u.id having -sum(t.amount) >= w.amount")
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        withdrawUsers = []
        for row in rows:
            withdrawUser = {}
            withdrawUser['id'] = row[0]
            withdrawUser['account'] = row[1]
            withdrawUser['amount'] = row[2]
            withdrawUsers.append(withdrawUser)
            self.cursor.execute("update transactions set status = 'Old' where account = %s and amount < %s", (row[1], 0))
            self.cursor.execute("delete from withdraw where id = %s", (row[0],))
        self.connection.commit()
        return withdrawUsers

    def getWithdrawList(self):
        self.cursor.execute("select u.name, w.account, w.amount from withdraw w, users u where w.id = u.id")
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        withdrawUsers = []
        for row in rows:
            withdrawUser = {}
            withdrawUser['name'] = row[0]
            withdrawUser['account'] = row[1]
            withdrawUser['amount'] = row[2]
            withdrawUsers.append(withdrawUser)
        return withdrawUsers

    def isEventEditable(self, eventId):
        self.cursor.execute("select id from events where id = %s and status in ('Active', 'Inactive')", (eventId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        return True

    def editEventTitle(self, eventId, newEventTitle):
        self.cursor.execute("update events set title = %s where id = %s", (newEventTitle, eventId))
        self.connection.commit()

    def existingBetsForEvent(self, eventId):
        self.cursor.execute("select id from bets where event_id = %s", (eventId,))
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return False
        return True

    def deleteEvent(self, eventId):
        self.cursor.execute("delete from events where id = %s", (eventId,))
        self.connection.commit()

    def rollbackEvent(self, eventId):
        self.cursor.execute("select user_id, sum(bet) from bets where event_id = %s group by user_id", (eventId,))
        rollbackRows = self.cursor.fetchall()
        rollbackUsers = []
        for userTotalBets in rollbackRows:
            self.cursor.execute("update users set balance = balance + %s where id = %s", (userTotalBets[1], userTotalBets[0]))
            rollbackUser = {}
            rollbackUser['id'] = userTotalBets[0]
            rollbackUser['bet'] = userTotalBets[1]
            rollbackUsers.append(rollbackUser)
        self.cursor.execute("delete from bets where event_id = %s", (eventId,))
        self.connection.commit()
        return rollbackUsers

    def getEventsToClose(self):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        self.cursor.execute("select id from events where status = 'Active' and close_when < %s", (now,))
        rows = self.cursor.fetchall()
        eventsToCloseIds = []
        for row in rows:
            eventsToCloseIds.append(row[0])
        return eventsToCloseIds

    def setCloseWhenForEvent(self, eventId, closeWhenTime):
        self.cursor.execute("update events set close_when = %s where id = %s", (closeWhenTime, eventId))
        self.connection.commit()

    def setCloseWhenForEventToNull(self, eventId):
        self.cursor.execute("update events set close_when = null where id = %s", (eventId,))
        self.connection.commit()

    def addAttachmentForApprove(self, messageId, userMention, userName):
        self.cursor.execute("insert into approve (id, mention, username) values (%s, %s, %s)", (messageId, userMention, userName))
        self.connection.commit()

    def getUserMentionByApproveId(self, messageId):
        self.cursor.execute("select mention from approve where id = %s", (messageId,))
        row = self.cursor.fetchall()
        if len(row) == 0:
            print('Getting user mention for approve has failed - no such approve message found in the database')
            return False
        return row[0][0]

    def deleteAttachmentForApprove(self, messageId):
        self.cursor.execute("delete from approve where id = %s", (messageId,))
        self.connection.commit()