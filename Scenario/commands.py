import random

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from Scenario.TheGame import TheGame
from Tools.DictAnagramSimple import AnagramKnow

MAIN_QUESTION, HELPER = range(2)

oracle_anagram = AnagramKnow()

keyboard_for_next = [
    ['Следующая', 'Главное меню']
]
for_next_markup = ReplyKeyboardMarkup(keyboard_for_next, one_time_keyboard=True)

keyboard_the_end = [
    ['Главное меню']
]
the_end_markup = ReplyKeyboardMarkup(keyboard_the_end, one_time_keyboard=True)

game_reply_keyboard = [
    ['Взять подсказку', 'Пропустить вопрос'],
    ['Закончить игру']
]
game_markup = ReplyKeyboardMarkup(game_reply_keyboard, one_time_keyboard=True)

game_cuting_reply_keyboard = [
    ['Пропустить вопрос', 'Закончить игру']
]
game_cuting_markup = ReplyKeyboardMarkup(game_cuting_reply_keyboard, one_time_keyboard=True)

main_reply_keyboard = [['/anagram', '/group'],
                       ['/game', '/help']]
main_markup = ReplyKeyboardMarkup(main_reply_keyboard, one_time_keyboard=True)


def start(update, context):
    update.message.reply_text('''*Доброго времени суток*\! Я бот\-помощник в мире анаграмм\. 
    *Анаграмма* \- это перестановка букв в слове, дающая новое слово\.''',
                              parse_mode='MarkdownV2')
    context.user_data['game'] = TheGame()
    help(update, context)


def help(update, context):
    update.message.reply_text('Я умею выполнять *команды*\:', parse_mode='MarkdownV2')
    update.message.reply_text('/anagram слово')
    update.message.reply_text(' Найти слово - анаграмму исходному, если оно есть.')
    update.message.reply_text('/group число')
    update.message.reply_text(
        ' Вывести группу анаграмм, c заданным числом слов.')
    update.message.reply_text('/game     ')
    update.message.reply_text('Игра на разгадывание анаграмм.')
    update.message.reply_text('/help')
    update.message.reply_text('Вывод справочной информации о командах бота.',
                              reply_markup=main_markup)


def game(update, context):
    update.message.reply_text(
        '''Добро пожаловать в *игру*\. Вам будет предложено 5 загадок\. 
        Постарайтесь отгадать слова, описанные в загадках\.''',
        parse_mode='MarkdownV2')
    update.message.reply_text('Вы всегда можете закончить игру словами "Закончить игру".')
    if 'game' not in context.user_data:
        context.user_data['game'] = TheGame()
    context.user_data['game'].make_new_game()
    update.message.reply_text('Вот первый вопрос.')
    for line in context.user_data['game'].get_question():
        update.message.reply_text(f'<b>{line}</b>', parse_mode='HTML')
    update.message.reply_text('В ответе должно быть только одно слово.', reply_markup=game_markup)
    return MAIN_QUESTION


def go_to_helper(update, context):
    context.user_data['was_helper'] = True
    update.message.reply_text('Вот подсказка.')
    update.message.reply_text(context.user_data['game'].get_helper())
    update.message.reply_text('Попробуйте отгадать теперь.', reply_markup=game_cuting_markup)
    return HELPER


def take_answer(update, context):
    user_answer = update.message.text
    reply_markup_local = game_cuting_markup if 'was_helper' in context.user_data else game_markup
    if "Взять подсказку" in user_answer and 'was_helper' in context.user_data:
        update.message.reply_text(
            'Подсказка уже была использована. Для каждого задания только одна подсказка.',
            reply_markup=reply_markup_local
        )
        return MAIN_QUESTION

    if context.user_data['game'].checking_answer(user_answer.lower()):
        context.user_data['game'].set_stats(True)
        update.message.reply_text(context.user_data['game'].get_phrase_for_ok_answer(),
                                  reply_markup=reply_markup_local)
        return go_to_next_task(update, context)
    else:
        context.user_data['game'].set_stats(False)
        update.message.reply_text(context.user_data['game'].get_phrase_for_wrong_answer())
        update.message.reply_text('Попробуйте еще раз!', reply_markup=reply_markup_local)
        return MAIN_QUESTION


def go_to_next_task(update, context):
    if context.user_data['game'].the_end():
        return stop_game(update, context)
    if 'was_helper' in context.user_data:
        del context.user_data['was_helper']
    context.user_data['game'].take_task()
    update.message.reply_text(f"Вопрос №{context.user_data['game'].pos_in_game}.")
    for line in context.user_data['game'].get_question():
        update.message.reply_text(f'<b>{line}</b>', parse_mode='HTML')
    update.message.reply_text('В ответе должно быть только одно слово.', reply_markup=game_markup)
    return MAIN_QUESTION


def stop_game(update, context):
    user_data = context.user_data
    update.message.reply_text('Спасибо за игру!')
    update.message.reply_text(
        f"<b>Вы отгадали {user_data['game'].score} из {user_data['game'].pos_in_game}.</b>",
        parse_mode='HTML', reply_markup=main_markup
    )
    return ConversationHandler.END


def show_answer(update, context):
    user_word = context.user_data['for_anagram']
    answer_oracle = oracle_anagram.get_anagram(user_word)
    if answer_oracle is None or len(answer_oracle) == 1 and user_word in answer_oracle:
        update.message.reply_text(
            f'Для слова <b>{user_word}</b> не найдено анаграмм, попробуйте ввести другое слово.',
            reply_markup=the_end_markup,
            parse_mode='HTML'
        )
        return 1
    сount_anagram = len(answer_oracle) - int(user_word in answer_oracle)
    if сount_anagram > 1:
        update.message.reply_text(f'Для слова <b>{user_word}</b> найдено несколько анаграмм:',
                                  parse_mode='HTML')
    else:
        update.message.reply_text(f'Для слова <b>{user_word}</b> найдена одна анаграмма -',
                                  parse_mode='HTML')
    for word in answer_oracle:
        if word != user_word:
            update.message.reply_text(f'<b>{word}</b>', parse_mode='HTML')
    update.message.reply_text('Чтобы сделать поиск анаграмм с новым словом, введите это слово.')
    update.message.reply_text(
        'Для возврата в главное меню введите или нажимте кнопку "Главное меню".',
        reply_markup=the_end_markup)
    return 1


def get_word(update, context):
    word = update.message.text
    if len(word.split()) != 1:
        update.message.reply_text(
            'Нужно ввести ровно одно слово. Введите его заново, пожалуйста.',
            reply_markup=the_end_markup)
        return 1
    context.user_data['for_anagram'] = word.strip().lower()
    return show_answer(update, context)


def anagram(update, context):
    if len(context.args) == 0:
        update.message.reply_text('Введите слово, для которого будем искать анаграмму',
                                  reply_markup=the_end_markup)
        return 1
    if len(context.args) > 1:
        update.message.reply_text('Нужно ввести ровно одно слово. Введите слово заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    context.user_data['for_anagram'] = context.args[0]
    return show_answer(update, context)


def stop_conversation(update, context):
    if 'masks_for_groups' in context.user_data:
        del context.user_data['masks_for_groups']
    if 'answer_oracle' in context.user_data:
        del context.user_data['answer_oracle']
    update.message.reply_text('Возвращаемся в главное меню.', reply_markup=main_markup)
    return ConversationHandler.END


def search_group(update, context):
    if len(context.args) == 0:
        update.message.reply_text('Введите количество слов в группе. Вводите число от 2 до 6.',
                                  reply_markup=the_end_markup)
        return 1
    if len(context.args) > 1:
        update.message.reply_text('Нужно ввести ровно одно число. Введите его заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    if not context.args[0].isnumeric():
        update.message.reply_text('Нужно ввести число, а не текст. Введите его заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    if not (2 <= int(context.args[0]) <= 6):
        update.message.reply_text('Нужно ввести число, от 2 до 6. Введите его заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    context.user_data['for_group'] = int(context.args[0])
    return show_group(update, context)


def get_number(update, context):
    number = update.message.text
    if len(number.split()) != 1:
        update.message.reply_text(
            'Нужно ввести ровно одно число. Введите его заново, пожалуйста.',
            reply_markup=the_end_markup)
        return 1
    if not number.strip().isnumeric():
        update.message.reply_text('Нужно ввести число, а не текст. Введите его заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    if not (2 <= int(number) <= 6):
        update.message.reply_text('Нужно ввести число, от 2 до 6. Введите его заново, пожалуйста.',
                                  reply_markup=the_end_markup)
        return 1
    context.user_data['for_group'] = int(number)
    return show_group(update, context)


def show_group(update, context):
    answer_oracle = None
    user_number = context.user_data['for_group']
    if 'masks_for_groups' not in context.user_data:
        user_number = context.user_data['for_group']
        answer_oracle = oracle_anagram.get_group(user_number)
        context.user_data['anwser_oracle'] = answer_oracle
        if answer_oracle is None or len(answer_oracle) == 1:
            update.message.reply_text(
                f'Для числа <b>{user_number}</b> не найдено группы анаграмм, введите другое число.',
                reply_markup=the_end_markup,
                parse_mode='HTML'
            )
            return 1
        update.message.reply_text(
            f'Для числа <b>{user_number}</b> групп анаграмм:  <b>{len(answer_oracle)}</b>',
            parse_mode='HTML'
        )
        for_shuffle = list(answer_oracle.keys())
        random.shuffle(for_shuffle)
        context.user_data['masks_for_groups'] = for_shuffle
    else:
        answer_oracle = context.user_data['anwser_oracle']

    key_for_dict = context.user_data['masks_for_groups'][0]
    context.user_data['masks_for_groups'] = context.user_data['masks_for_groups'][1:]
    searched_group = answer_oracle[key_for_dict]
    update.message.reply_text('Вот одна из групп анаграмм:')
    for word in searched_group:
        update.message.reply_text(f'<b>{word}</b>', parse_mode='HTML')
    if len(context.user_data['masks_for_groups']) == 0:
        if 'masks_for_groups' in context.user_data:
            del context.user_data['masks_for_groups']
        if 'answer_oracle' in context.user_data:
            del context.user_data['answer_oracle']
        update.message.reply_text(
            'Это была последняя группа. Возвращаемся в главное меню".',
            reply_markup=main_markup)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            f'Чтобы перейти к следующей группе с количеством слов {user_number} нажимте "Следующая".')
        update.message.reply_text(
            'Для возврата в главное меню введите или нажимте кнопку "Главное меню".',
            reply_markup=for_next_markup)
    return 2
