from Scenario.commands import start, help, game, stop_game, go_to_helper, take_answer, go_to_next
from tlg_token import TOKEN
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from Scenario.commands import MAIN_QUESTION, HELPER, SUBQUESTION
from data import db_session
import logging

PATH_DB = 'db/anagram.sqlite'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    start_command = CommandHandler('start', start)
    help_command = CommandHandler('help', help)
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
                    Filters.text & ~(Filters.command | Filters.regex('^Закончить игру$')),
                    take_answer
                ),
                MessageHandler(Filters.regex("^Пропустить вопрос$"), go_to_next)
            ],
            # Функция читает ответ на второй вопрос и завершает диалог.
            HELPER: [MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Закончить игру$')),
                    take_answer
                ),
                MessageHandler(Filters.regex("^Пропустить вопрос$"), go_to_next)
            ]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[MessageHandler(Filters.regex('^Закончить игру$'), stop_game)]
    )

    dp.add_handler(start_command)
    dp.add_handler(help_command)
    dp.add_handler(conv_handler)
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    db_session.global_init(PATH_DB)
    main()
