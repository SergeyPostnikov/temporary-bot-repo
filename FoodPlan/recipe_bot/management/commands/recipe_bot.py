import logging

from django.apps import apps
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from pathvalidate import sanitize_filename
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.error import NetworkError
from telegram.ext import CallbackQueryHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater


logger = logging.getLogger(__file__)


APP_NAME = 'recipe_bot'


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO,
                            filename='recipe_bot.log',
                            filemode='w'
        )
        self.updater = Updater(token=settings.TELEGRAM_BOT_TOKEN)
        bot_text_handler = MessageHandler(Filters.text | Filters.command, self.bot_text_handler)
        self.updater.dispatcher.add_handler(bot_text_handler)
        bot_button_handler = CallbackQueryHandler(self.bot_button_handler)
        self.updater.dispatcher.add_handler(bot_button_handler)

        self.methods = {
            'consent_pdf_sending': self.publish_consent_pdf,
            'username_getting': self.get_user_name,
        }
        self.dialogue_point = 'start'
        self.username = ''

    def handle(self, *args, **kwargs):
        self.updater.start_polling()
        self.updater.idle()

    def bot_text_handler(self, update, context):
        if update.channel_post.text == '/start':
            self.dialogue_point = 'start'
            self.username = ''
            self.send_greeting_invitation(update, context)
            return

        self.methods[self.dialogue_point](update, context)

    def bot_button_handler(self, update, context):
        # Обязательная команда (см. https://core.telegram.org/bots/api#callbackquery)
        update.callback_query.answer()
        self.methods[self.dialogue_point](update, context)

    def send_greeting_invitation(self, update, context):
        question = ('Рад встрече!\n'
                    'Я могу подбирать для вас рецепты блюд.\n'
                    'Заинтересовались?\n'
                    'Давайте познакомимся.\n'
                    'Мы хотим настроить свои предложения индивидуально для вас.\n'
                    'Для этого нам будут нужны ваше имя и телефон.\n'
                    'Хотите прочитать наше Соглашение об обработке персональных данных?'
        ) 
        keyboard = [
             [
                 InlineKeyboardButton('Да', callback_data='да'),
                 InlineKeyboardButton('Нет', callback_data='нет'),
             ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.dialogue_point = 'consent_pdf_sending'
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=question, reply_markup=reply_markup)    

    def publish_consent_pdf(self, update, context):
        if self.dialogue_point != 'consent_pdf_sending':
            return

        query = update.callback_query
        variant = query.data
        if variant == 'нет':
            return

        consent_pdf_filename = 'Consent_Of_Personal_Data_Processing.pdf'
        app_dirpath = apps.get_app_config(APP_NAME).path
        static_subfolder = settings.STATIC_URL.strip('/')
        pdf_subfolder = 'pdf'
        consent_pdf_filepath = Path(app_dirpath) / static_subfolder / pdf_subfolder / consent_pdf_filename

        delay = 1
        while True:
            try:
                context.bot.send_document(chat_id=update.effective_chat.id,
                                          document=open(consent_pdf_filepath, 'rb'))
                message_start = f'Согласны?\n'
                self.send_username_input_invitation(update, context, message_start)
                return
            except FileNotFoundError as ex:
                logger.warning(ex)
                logger.warning(f'Нет файла {pdf_filepath}')
                return
            except NetworkError as ex:
                logger.warning(ex)
                time.sleep(delay)
                delay = 10
            except Exception as ex:
                logger.warning(ex)
                return

    def send_username_input_invitation(self, update, context, message_start=''):
        message = f'{message_start}Введите ваше имя:'
        self.dialogue_point = 'username_getting'
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    def get_user_name(self, update, context):
        if self.dialogue_point != 'username_getting':
            return

        username = update.channel_post.text
        is_good_username = bool(username)
        if is_good_username:
            usernames = [sanitize_filename(name.strip()).capitalize() for name in username.split()]
            username = ' '.join(usernames)
            is_good_username = len(username) > 2

        if not is_good_username:
            self.send_username_input_invitation(update, context, message_start='Неправильное имя.\n')

        self.username = username
        self.send_username_phone_invitation(update, context)

    def send_username_phone_invitation(self, update, context):
        pass
       