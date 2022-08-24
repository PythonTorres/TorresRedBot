import os

from discord.ext.commands import cog

#config file for the main bot.py and all the cogs

bot = {
    'prefix': '.',
    'owner': 252467288064655360,
    'token': 'NDgzOTY5Nzc4Nzc2ODAxMjgx.W4U5-g.huEa6p5zpyHaCZc12aUdpKW3J2o'
}

cogAutoReactions = {
    'textChannel': 347205730455257089 #news (347205730455257089)
}

cogInterviewAccess = {
    'voiceChannel': 347243470882340865, #⛔ Тихо! 📢 ОБЗВОН! (347243470882340865)
    'textChannel': 777552100481433630, #interview_chat (777552100481433630)
    'ignoredRoles': set([
        347183694017986560, # Администратор
        347191653422989312, # Агент поддержки
        352807753653157888, # Модератор
        632944482689613865, # Следящий за МВД
        352128041939632135, # Младший модератор
        371927987643351052, # Игровой администратор
        352109351223296000, # Мин. внутренних дел
        428779838871175170  # Пом. Мин. внутренних дел
        ])
}

cogBets = {
    'accessEvents': [252467288064655360, 417316579366404107], #me and rufan
    'dataBaseURL': os.environ['DATABASE_URL'],
    'betsRoleId': 871382213567082556, #Bets
    'betGuildId': 347180250079166464, #ADVANCE RP RED SERVER
    'archiveTextChannel': 871373385635102720, #events_archive
    'registrationTextChannel': 871372207824187402, #registration
    'checkRegistrationAndNewTransactionsLoopTime': 25,
    'checkForExpiredRegLoopTime': 3600,
    'checkForExpiredWaitForBetLoopTime': 80,
    'checkWithdrawLoopTime': 1900,
    'checkForCloseEventTime': 150,
    'RegsAreExpiredAfterMinutes': 120,
    'WaitForBetExpiredAfterMinutes': 5,
    'registrationText': 'Добро пожаловать в ставки! Для регистрации в системе нажмите на кнопку ниже.',
    'registrationAlreadyRegisteredResponseText': 'Вы уже зарегистрированы в системе',
    'registrationAlreadyInProgressResponseText': 'Процесс регистрации уже запущен для Вас, инструкции предоставлены в личном сообщении от бота',
    'registrationResponseText': 'Бот отправил Вам личное сообщение, проверьте его для продолжения регистрации',
    'registrationFailResponseText': 'Бот не может отправить Вам личное сообщение, измените настройки приватности и попробуйте еще раз',
    'registrationMessageTextStart': 'Добро пожаловать в ставки!\n\nДля завершения регистрации совершите перевод **со своего ДОПОЛНИТЕЛЬНОГО счета (который имеет НОМЕР СЧЕТА)** на счет 86302 в размере $',
    'registrationMessageTextEnd': '.\n\nНе переживайте, эта сумма будет зачислена на Ваш баланс автоматически, она служит для регистрации Вашего счета в системе.\n\n**ВНИМАНИЕ!** Счет, с которого будет совершен перевод, будет закреплен за Вами в системе. Пополнение баланса и вывод средств в дальнейшем будет происходить с использованием **именно этого** счета.',
    'registrationMessageRegReminderText': 'Напоминаем, для завершения регистрации совершите перевод **со своего дополнительного счета (который имеет номер счета)** на счет 86302 в размере $',
    'registrationSuccessfulMessageText': 'Регистрация прошла успешно!\n\nВы зарегистрированы в системе со счетом {}.\nНа Ваш аккаунт было успешно зачислено ${}.\n\nДля пополнения баланса совершите перевод со своего зарегистрированного счета на счет 86302 в любом размере.\n\nЖелаем Вам приятной игры!',
    'registrationExpiredMessageText': 'Ваш процесс регистрации был остановлен, так как указанного перевода не было получено.\nВы можете запустить процесс регистрации тем же способом, что и в прошлый раз.',
    'balanceIncreaseMessageText': 'Обнаружено пополнение баланса с Вашего счета на общую сумму ${}\nВаш баланс: **${}**',
    'eventDescriptionText': 'Исходы события и их коэффициенты представлены ниже. Чтобы сделать ставку, выберите исход из списка.',
    'eventArchivedDescriptionText': 'Событие в архиве. Выплаты произведены.',
    'eventArchivedWinnerAddition': ' (победитель)',
    'eventFooterText': 'Автор события: {}',
    'eventSelectPlaceholderText': 'Выберите исход события',
    'eventDisabledSelectPlaceholderText': 'Ставки закрыты',
    'eventCannotSummarizeNotInactiveMessageText': 'Событие не закрыто, невозможно подвести итоги',
    'eventCannotCloseNotActiveEventMessageText': 'Событие не активно. Невозможно закрыть.',
    'eventCannotSummarizeWaitingBetsMessageText': 'Невозможно подвести итоги сейчас. Ожидаются ставки: {}',
    'eventCannotSummarizeCannotFetchEventMessageText': 'Невозможно подвести итоги. Сообщение события не найдено.',
    'eventSummarizeChooseWinnerMessageText': 'Выберите победный исход из списка',
    'eventSummarizeConfirmMessageText': 'Событие: **{}**\nПобедный исход: **{}**\nСумма ставок: **{}**\nПодтвердите выплату победителям и архивацию события.',
    'eventSummarizeConfirmCanceledMessageText': 'Отменено. Итоги не подведены.',
    'eventSummarizeConfirmedMessageText': 'Подтверждение получено, подводим итоги события.',
    'eventSummarizeConfirmRollbackMessageText': 'Условия для выплаты выигрыша не выполнены. Ставки возвращены.',
    'eventSummarizeWinnersPartText': '{} выиграл ${}\n',
    'eventSummarizeConfirmedAndPayedMessageText': 'Выплаты победителям успешно осуществлены',
    'eventEventHasBeenClosedMessageText': 'Событие **{}** успешно закрыто.',
    'eventCannotOpenNotInactiveEventMessageText': 'Событие не в статусе Неактивно. Невозможно открыть.',
    'eventEventHasBeenOpenedMessageText': 'Событие **{}** успешно открыто.',
    'eventEditImpossibleMessageText': 'Событие с id {} невозможно отредактировать.\nСобытие не найдено или находится в невозможном для редактирования статусе.',
    'eventDeleteImpossibleBetsWaitingMessageText': 'Событие с id {} невозможно удалить.\nОжидаются ставки на событие в количестве: {}\nНеобходимо закрыть ставки, дождаться сброса ожидания ставок, а потом попробовать удалить событие еще раз.',
    'eventDeleteImpossibleBetsExistMessageText': 'Событие с id {} невозможно удалить.\nПрисутствуют ставки на событие.\nНеобходимо закрыть событие, после чего совершить откат ставок.',
    'eventDeleteImpossibleEventNotClosedMessageText': 'Событие с id {} невозможно удалить. Событие не закрыто.',
    'eventRollbackImpossibleBetsWaitingMessageText': 'Событие с id {} невозможно откатить.\nОжидаются ставки на событие в количестве: {}\nНеобходимо закрыть ставки, дождаться сброса ожидания ставок, а потом попробовать откатить событие еще раз.',
    'eventRollbackImpossibleEventNotClosedMessageText': 'Событие с id {} невозможно откатить. Событие не закрыто.',
    'eventRollbackMessageStartText': 'Ставки на событие с id {}, название: **{}** возвращены на счет пользователям.',
    'eventRollbackMessagePieceText': '\nПользователю {} возвращено ${}',
    'eventCloseWhenCannotBeConvertedMessage': 'Дата закрытия не может быть преобразована. Неправильный формат. Пример: "01.01.2021 02:03"',
    'eventCloseWhenIsSetMessage': 'Событие **{}** будет закрыто {}',
    'eventCloseWhenCannotBeSetAsEventIsNotActiveMessage': 'Дата закрытия для события **{}** не может быть установлена, так как событие не Активно.',
    'eventCloseWhenCannotBeSetAsEventNotFoundMessage': 'Дата закрытия для события не может быть установлена, так как событие не найдено в базе данных.',
    'eventCloseWhenSetDuringCreationMessage': 'Время закрытия для события **{}** установлено как **{}**',
    'betUserNotRegisteredText': 'Вы не зарегистрированы в системе',
    'betEventNotFoundText': 'Событие не активно или не найдено',
    'betEventCheckDMToConfirmText': 'Написал Вам в личные сообщения',
    'betAskForBetText': 'Событие: **{}**\nИсход: **{}**\nВаш баланс: **${}**\nЧтобы сделать ставку, напишите сумму. Например, 5000\nЧтобы не делать ставку, напишите 0',
    'betAskForCorrectValueText': 'Ожидается корректная сумма (только число), например, 5000',
    'betWaitForBetCancelledText': 'Ожидание ставки отменено.\nЧтобы сделать ставку, выберите исход еще раз.',
    'betWaitForBetInProgressText': 'Сумма ставки ожидается в личных сообщениях, сообщите её или выберите Снять выделение, а потом исход из списка',
    'betWaitForBetRemovedText': 'Отменил ожидание ставки на прошлый вариант. Чтобы сделать ставку, выберите исход снова.',
    'betAskForPositiveValueText': 'Ожидается положительная сумма, например, 5000',
    'betBalanceLowerThanBetText': 'На Вашем балансе недостаточно средств для совершения такой ставки, попробуйте меньшую сумму',
    'betDefaultExceptionMessageText': 'Во время обработки ставки произошла ошибка, попробуйте еще раз',
    'betSuccessMessageText': 'Ваша ставка в размере **${}** принята',
    'betExpiredMessageText': 'Вы не указали сумму ставки. Чтобы сделать ставку, выберите исход еще раз.',
    'betForbiddenErrorText': 'Бот не может отправить Вам личное сообщение, измените настройки приватности и попробуйте еще раз',
    'betFieldDescriptionText': 'Коэффициент: {coef}\nСумма ставок: ${sum}\n ',
    'betOptionDescriptionText': 'Коэф. {coef}, Ставок: ${sum}',
    'betFieldCoefDefaultText': '-',
    'betRollbackNotifyMessageText': 'Ваша ставка на событие **{}** была возвращена на счет\nОбщая сумма: **${}**\nВаш баланс: **${}**',
    'betWinNotifyMessageText': 'Поздравляем!\nВаша ставка на событие **{}**, исход **{}** выиграла!\nОбщий выигрыш: **${}**\nВаш баланс: **${}**',
    'withdrawNotRegisteredMessageText': 'Вы не зарегистрированы в системе ставок.',
    'withdrawZeroBalanceMessageText': 'Ваш баланс нулевой. Нечего выводить.',
    'withdrawIncorrectAmountMessageText': 'Введено неверное значение для вывода.\nПример команды: ' + bot['prefix'] + 'withdraw 5000',
    'withdrawNegativeAmountMessageText': 'Значение для вывода должно быть положительным.\nПример команды: ' + bot['prefix'] + 'withdraw 5000',
    'withdrawAmountGreaterThanBalanceMessageText': 'На Вашем балансе недостаточно средств для вывода такой суммы. Попробуйте ввести меньшую сумму.',
    'withdrawCreatedMessageText': 'Заявка на вывод средств принята.\nОбщая сумма для вывода: **${}**\nЗапрошенные средства списаны с баланса. Вы получите уведомление, когда они будут перечислены на Ваш игровой счет (который использовался для пополнения баланса).\nВаш баланс: **${}**',
    'withdrawSuccessMessageText': 'Ваша заявка на вывод средств выполнена.\n**${}** переведены на Ваш счет {}',
    'withdrawListNoItemsMessageText': 'Нет активных заявок на вывод средств',
    'withdrawListStartText': '**Активные заявки на вывод средств:**',
    'withdrawListItemText': '\nСумма: **${}**, Счет: **{}**, Пользователь: {}'
}

bankTransactions = {
    'loopTime': 15,
	'driverPath': './chromedriver',
    'dataBaseURL': os.environ['DATABASE_URL']
}

cogAttachmentApprove = {
    'textChannel': 951289866388381766, #censorship
    'outChannel': 347180250079166465, #general_chat
    'approversUsers': [252467288064655360, 252467288064655360, 252467288064655360], #mememe
    'messageWhenSentForApprove': '{userMention} прислал вложение на аппрувчик:',
    'messageWhenApproved': 'by {userMention}'
}

# 1 is for production (heroku) and 0 is for testing (windows)
setEnviroment = 1

try:
    if setEnviroment == 1:
        pass
    elif setEnviroment == 0:
        bot['prefix'] = ','
        bot['token'] = 'NTc4NjgwNjQ5NTMyMDQ3MzYw.XN3IWg._1UQy7Int6HVJlqLchKpbEIohYM' #rufanEbalo
        cogAutoReactions['textChannel'] = 866317629677371402 #autoreactions
        cogInterviewAccess['textChannel'] = 866317629677371402 #autoreactions
        cogInterviewAccess['voiceChannel'] = 809822754425536513 #sigame 00/69
        cogBets['registrationTextChannel'] = 867163536400056323 #bets-reg on bets alfa test server (866335641268125696 - for test server)
        cogBets['dataBaseURL'] = 'postgres://wbcdkeipinbcsp:bb30db227ed45e2c2f4707919378c99b0ea1758368960da85f36d565592f37c6@ec2-34-254-69-72.eu-west-1.compute.amazonaws.com:5432/d8b05snfrgatvb'
        cogBets['RegsAreExpiredAfterMinutes'] = 1 
        cogBets['checkForExpiredRegLoopTime'] = 20
        cogBets['WaitForBetExpiredAfterMinutes'] = 2
        cogBets['checkWithdrawLoopTime'] = 20 #seconds
        cogBets['archiveTextChannel'] = 870447583921852426 #mod-mail 578612573788831745 bets-archive 870447583921852426
        cogBets['betsRoleId'] = 871404097260126269 #Bets test
        cogBets['betGuildId'] = 867163536400056320 #Ставки Альфа Тест
        bankTransactions['driverPath'] = 'C:\\WebDrivers\\chromedriver.exe'
        bankTransactions['dataBaseURL'] = 'postgres://wbcdkeipinbcsp:bb30db227ed45e2c2f4707919378c99b0ea1758368960da85f36d565592f37c6@ec2-34-254-69-72.eu-west-1.compute.amazonaws.com:5432/d8b05snfrgatvb'
        cogAttachmentApprove['textChannel'] = 950770767434485810 #approve
        cogAttachmentApprove['outChannel'] = 479947539345571844 #general (Test Server)
    else:
        print('ENVIROMENT IS NOT SELECTED')
except:
    print('ERROR IN ENVIROMENT SELECTION')
    raise