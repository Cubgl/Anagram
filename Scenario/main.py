from Scenario.commands import *
from tlg_token import TOKEN
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from data import db_session
import logging

PATH_DB = '../db/anagram.sqlite'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    start_command = CommandHandler('start', start)
    help_command = CommandHandler('help', help)
    anagram_handler = ConversationHandler(
        entry_points=[CommandHandler('anagram', anagram, pass_args=True)],
        states={
            1: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Главное меню$')),
                               get_word
                               ),
                CommandHandler('anagram', anagram, pass_args=True)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Главное меню$'), stop_conversation)]
    )
    group_handler = ConversationHandler(
        entry_points=[CommandHandler('group', search_group, pass_args=True)],
        states={
            1: [
                MessageHandler(Filters.text & \
                               ~(Filters.command | Filters.regex('^Главное меню$') | \
                                 Filters.regex('^Следующая$')), get_number),
                CommandHandler('group', search_group, pass_args=True)
            ],
            2: [MessageHandler(Filters.regex('^Следующая$'), show_group)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Главное меню$'), stop_conversation)]
    )
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('game', game)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            MAIN_QUESTION: [
                MessageHandler(Filters.regex("^Взять подсказку$"), go_to_helper),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex("^Пропустить вопрос$") | \
                                     Filters.regex('^Закончить игру$')),
                    take_answer
                ),
                MessageHandler(Filters.regex("^Пропустить вопрос$"), go_to_next_task)
            ],
            # Функция читает ответ на второй вопрос и завершает диалог.
            HELPER: [MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex("^Пропустить вопрос$") | \
                                 Filters.regex('^Закончить игру$')),
                take_answer
            ),
                MessageHandler(Filters.regex("^Пропустить вопрос$"), go_to_next_task)
            ]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[MessageHandler(Filters.regex('^Закончить игру$'), stop_game)]
    )

    dp.add_handler(start_command)
    dp.add_handler(help_command)
    dp.add_handler(conv_handler)
    dp.add_handler(anagram_handler)
    dp.add_handler(group_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    db_session.global_init(PATH_DB)
    main()
