"""
This is medicine bot, which includes some tests.
When you start working with this bot you should enter secret login and password.
"""

import tests
import logging, random
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove,\
    InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler,\
    CallbackQueryHandler, Filters


NAME = "chatsky_test_2bot"
API = "660506337:AAG6LsMsWl1UvnrasIiN8cJgSW9ni7fo3kA"
PROXY = {'proxy_url': 'socks5://163.172.152.192:1080'}

admin_id = 0
authorized = False

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)


def get_passinfo(directory):
    with open(directory, "r") as f:
        login_ = f.readline()[:-1]
        password_ = f.readline()

    return login_, password_


def start(bot, update):
    greetings = """Привет, юзер!
Я ВрачБот, помогу тебе предупредить проблемы со здоровьем!
Чтобы начать разговор со мной, введи команду /login
Чтобы увидеть список моих комманд, напиши /help"""

    bot.send_message(chat_id=update.message.chat_id, text=greetings)


def login(bot, update, args):
    global authorized, admin_id
    succes_text = "Привет, администратор, я наконец-то тебя распознал!"
    error_text = "Извини, но я тебя не помню. Попробуй ещё раз"

    if update.message.chat_id == admin_id:
        bot.send_message(chat_id=update.message.chat_id, text=succes_text)
        return

    if len(args) == 2:
        if args[0] == login_ and args[1] == password_:
            admin_id = update.message.chat_id

            with open("chat_id.txt", "w") as f:
                f.write(str(admin_id))

            bot.send_message(chat_id=update.message.chat_id, text=succes_text)
            authorized = True
            return

    authorized = False
    bot.send_message(chat_id=update.message.chat_id, text=error_text)


def main_menu(bot, update):
    keyboard =[
        [InlineKeyboardButton("Тест мозговой активности", callback_data="brain_test"),
         InlineKeyboardButton("Второй тест", callback_data="test2")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Выбери тест, который ты хотел бы пройти.",
                     reply_markup=reply_markup)


def sticker(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=random.choice(
        ["Какой классный стикер!", "Мне нравится этот стикерпак.",
         "Выглядит восхитительно!"]))


def test_choose(bot, update):
    global brain_test, updater
    query = update.callback_query

    if query.data == "brain_test":
        brain_test = tests.BrainTest(updater, admin_id)
        test_handlers.append(brain_test.handler)
        brain_test.ask(bot, query)

    elif query.data == "test2":
        bot.send_message(chat_id=query.message.chat_id, text="test2")


def clean(bot, update):
    for handler in test_handlers:
        dispatcher.remove_handler(handler)

    bot.send_message(chat_id=update.message.chat_id,
                     reply_markup=ReplyKeyboardRemove())


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Мяу-мяу, миу мяу мяу! Я тебя не понимаю, "
                          "посмотри доступные комманды с помощью /help.")


if __name__ == "__main__":
    with open("chat_id.txt", "r") as f:
        admin_id = int(f.readline())

    login_, password_ = get_passinfo("passinfo.txt")

    updater = Updater(token=API)
    dispatcher = updater.dispatcher

    test_handlers = []

    command_functions = [start, main_menu, clean]
    for funct in command_functions:
        dispatcher.add_handler(CommandHandler(funct.__name__.lower(), funct))

    dispatcher.add_handler(CommandHandler("login", login, pass_args=True))

    dispatcher.add_handler(CallbackQueryHandler(test_choose))

    dispatcher.add_handler(MessageHandler(Filters.sticker, sticker))

    # This one have to be the last handler, or other handlers won't work.
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()