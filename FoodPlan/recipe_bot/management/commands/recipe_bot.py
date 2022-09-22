import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from .dialog_bot import DialogBot


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO,
                            filename='recipe_bot.log',
                            filemode='w'
        )

    def handle(self, *args, **kwargs):
        dialog_bot = DialogBot(settings.TELEGRAM_BOT_TOKEN, self.bot_generator)
        dialog_bot.start()

    def bot_generator(self):
        question = ('Рад встрече!\n'
                    'Я могу подбирать для вас рецепты блюд.\n'
                    'Заинтересовались?\n'
                    'Давайте познакомимся.\n'
                    'Мы хотим настроить свои предложения индивидуально для вас.\n'
                    'Для этого нам будут нужны ваше имя и телефон.\n'
                    'Хотите прочитать наше Соглашение об обработке персональных данных?'
        )
        likes_python = yield from self.ask_yes_or_no(question)

    def ask_yes_or_no(self, question):
        keyboard = [
             [
                 InlineKeyboardButton('Да', callback_data='да'),
                 InlineKeyboardButton('Нет', callback_data='нет'),
             ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        answer = yield question, reply_markup
        # while not ("да" in answer.text.lower() or "нет" in answer.text.lower()):
        #     answer = yield (question, reply_markup)
        # return "да" in answer.text.lower()
