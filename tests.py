import logging
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)


class Test(object):
    def __init__(self, updater, args, admin_id):
        self.admin_id = admin_id

        self.updater = updater
        self.dispatcher = updater.dispatcher

        self.handler = MessageHandler(Filters.text, self.ask)
        self.dispatcher.add_handler(self.handler)

        self.test = args
        self.result = []

        self.flag = False

    def start(self, bot, update):
        pass

    def end(self, bot, update):
        pass

    def ask(self, bot, update):
        if self.flag:
            self.result.append(update.message.text)

        else:
            self.start(bot, update)
            self.flag = True

        if len(self.test) > 0:
            for question in self.test:
                answer = self.test.pop(question)
                if answer == [[""]] or answer == [["False"]]:
                    bot.send_message(chat_id=update.message.chat_id,
                                     text=question)

                else:
                    bot.send_message(chat_id=update.message.chat_id,
                                     text=question,
                                     reply_markup=ReplyKeyboardMarkup(
                                         answer, one_time_keyboard=True))

                break

        else:
            self.dispatcher.remove_handler(self.handler)
            self.end(bot, update)


class BrainTest(Test):
    def __init__(self, updater, admin_id):
        test = get_test("tests/brain_test/test.txt")
        super(BrainTest, self).__init__(updater, test, admin_id)

        self.verdict = [{"danger": 0, "text": ""} for i in range(7)]
        self.get_verdict()

    def get_verdict(self):
        with open(r"tests\brain_test\test_verdict.txt") as f:
            i = 0
            for line in f:
                if "/end/" in line:
                    self.verdict[i]["text"] += line.replace("/end/", "")
                    i += 1

                else:
                    self.verdict[i]["text"] += line

    def start(self, bot, update):
        greetings = ""

        with open(r"tests\brain_test\test_introduction.txt", "r") as f:
            for line in f:
                greetings += line

        bot.send_message(chat_id=update.message.chat_id, text=greetings)

    def end(self, bot, update):
        for i in range(7):
            for ii in range(10):
                j = i*10 + ii

                if int(self.result[j]) > 2:
                    self.verdict[i]["danger"] += 1

        print(self.verdict)

        # that's one of brain test's trait
        if self.verdict[0]["danger"] >= 3:
            temp = self.verdict.pop(0)

        else:
            temp = False

        sorted(self.verdict, key=lambda item: item["danger"])
        if temp:
            self.verdict.insert(0, temp)

        for elem in self.verdict:
            if elem["danger"] >= 2:
                if elem["danger"] == 2:
                    text = "\nЕсть некоторая вероятность проблем"
                    bot.send_message(chat_id=update.message.chat_id, text=text)

                elif elem["danger"] == 3:
                    text = "\nПроблемы вероятны"
                    bot.send_message(chat_id=update.message.chat_id, text=text)

                else:
                    text = "\nПроблемы очень вероятны"
                    bot.send_message(chat_id=update.message.chat_id, text=text)

                bot.send_message(chat_id=update.message.chat_id,
                                 text=elem["text"])


def get_test(directory):
    test = {}
    flag = False
    temp = 0
    with open(directory, "r") as f:
        for line in f:
            if flag:
                test[temp] = [line[:-1].split("_")]
                flag = False

            else:
                temp = line[:-1]
                flag = True

    return test


