import collections
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
# from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

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
        self.updater = Updater(token=settings.TELEGRAM_BOT_TOKEN)
        bot_messages_handler = MessageHandler(Filters.text | Filters.command, self.bot_messages_handler)
        self.updater.dispatcher.add_handler(bot_messages_handler)
        bot_buttons_handler = CallbackQueryHandler(self.bot_buttons_handler)
        self.updater.dispatcher.add_handler(bot_buttons_handler)

    def handle(self, *args, **kwargs):
        self.updater.start_polling()
        self.updater.idle()

    def bot_messages_handler(self, update, context):
        if update.channel_post.text != "/start":
            return

        question = ('Рад встрече!\n'
                    'Я могу подбирать для вас рецепты блюд.\n'
                    'Заинтересовались?\n'
                    'Давайте познакомимся.\n'
                    'Мы хотим настроить свои предложения индивидуально для вас.\n'
                    'Для этого нам будут нужны ваше имя и телефон.\n'
                    'Хотите прочитать наше Соглашение об обработке персональных данных?'
        )
        # context.bot.send_message(chat_id=update.effective_chat.id, 
        #                          text=question)        
        keyboard = [
             [
                 InlineKeyboardButton('Да', callback_data='да'),
                 InlineKeyboardButton('Нет', callback_data='нет'),
             ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=question, reply_markup=reply_markup)

    def bot_buttons_handler(self, update, _):
        query = update.callback_query
        variant = query.data
        print(variant)

        # `CallbackQueries` требует ответа, даже если 
        # уведомление для пользователя не требуется, в противном
        #  случае у некоторых клиентов могут возникнуть проблемы. 
        # смотри https://core.telegram.org/bots/api#callbackquery.
        query.answer()
        # редактируем сообщение, тем самым кнопки 
        # в чате заменятся на этот ответ.
        # query.edit_message_text(text=f"Выбранный вариант: {variant}")

        # likes_python = yield from self.ask_yes_or_no(question)
        # print(likes_python)
        # if likes_python:
        #     answer = yield from discuss_good_python(name)
        # else:
        #     answer = yield from discuss_bad_python(name)

    # def ask_yes_or_no(self, question):
    #     keyboard = [
    #          [
    #              InlineKeyboardButton('Да', callback_data='да'),
    #              InlineKeyboardButton('Нет', callback_data='нет'),
    #          ],
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     answer = yield question, reply_markup
    #     return answer
