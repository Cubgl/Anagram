from telegram import ReplyKeyboardMarkup

from Scenario.TheGame import TheGame

MAIN_QUESTION, HELPER, SUBQUESTION = range(3)

game_reply_keyboard = [
    ['Взять подсказку', 'Пропустить вопрос'],
    ['Закончить игру']
]
game_markup = ReplyKeyboardMarkup(game_reply_keyboard, one_time_keyboard=True)

game_cuting_reply_keyboard = [
    ['Пропустить вопрос'],
    ['Закончить игру']
]
game_cuting_markup = ReplyKeyboardMarkup(game_reply_keyboard, one_time_keyboard=True)

main_reply_keyboard = [['/anagram', '/group'],
                       ['/game', '/cod'],
                       ['/close']]
main_markup = ReplyKeyboardMarkup(main_reply_keyboard, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(' *Доброго времени суток*\! Я бот\-помощник в мире анаграмм\.',
                              parse_mode='MarkdownV2')
    update.message.reply_text('*Анаграмма* \- это перестановка букв в слове, дающая новое слово\.',
                              parse_mode='MarkdownV2')
    help(update, context)


def help(update, context):
    update.message.reply_text('Я умею выполнять *команды*\:', parse_mode='MarkdownV2')
    update.message.reply_text('/anagram слово')
    update.message.reply_text(' Найти слово, которое является анаграммой исходному, если оно есть.')
    update.message.reply_text('/group число')
    update.message.reply_text(
        ' Вывести группу анаграмм, в которой количество слов равно заданному числу.')
    update.message.reply_text('/game')
    update.message.reply_text(' Игра на разгадывание анаграмм.')
    update.message.reply_text('/cod фраза')
    update.message.reply_text(
        ''' Кодирование фразы анаграммой. Попробуйте закодировать свои фамилию и имя.''')
    update.message.reply_text('/close')
    update.message.reply_text('Выход', reply_markup=main_markup)


def game(update, context):
    update.message.reply_text(
        '''Добро пожаловать в *игру*\. Вам будет предложено 5 загадок. 
        Постарайтесь отгадать слова, описанные в загадках\.''',
        parse_mode='MarkdownV2')
    update.message.reply_text('Вы всегда можете закончить игру словами "Закончить игру".')
    context.user_data['game'] = TheGame()
    update.message.reply_text('Вот первый вопрос.')
    for line in context.user_data['game'].get_question():
        update.message.reply_text(line)
    update.message.reply_text('В ответе должно быть только одно слово.', reply_markup=game_markup)
    return MAIN_QUESTION


def go_to_helper(update, context):
    update.message.reply_text('Вот подсказка.')
    update.message.reply_text(context.user_data['game'].get_helper(), reply_markup=game_cuting_markup)
    update.message.reply_text('Попробуйте отгадать теперь.')
    return SUBQUESTION


def take_answer(update, context):
    user_answer = update.message.text
    if user_answer.lower() == context.user_data['game'].get_answer():
        context.user_data['game'].set_stats(True)
    else:
        context.user_data['game'].set_stats(False)



def stop_game(update, context):
    user_data = context.user_data
    update.message.reply_text('Спасибо за игру!')
    update.message.reply_text(
        "Вы отгадали {user_data['game'].score} из {user_data['game'].pos_in_game}.")