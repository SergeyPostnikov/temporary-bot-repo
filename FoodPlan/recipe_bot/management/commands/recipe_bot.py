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
        bot_text_handler = MessageHandler(Filters.text | Filters.command, self.handle_bot_text)
        self.updater.dispatcher.add_handler(bot_text_handler)
        bot_button_handler = CallbackQueryHandler(self.handle_bot_button)
        self.updater.dispatcher.add_handler(bot_button_handler)

        self.dialogue_point = 'start'
        self.username = ''
        self.user_phone = ''
        self.current_handler = None

    def handle(self, *args, **kwargs):
        self.updater.start_polling()
        self.updater.idle()

    def handle_bot_text(self, update, context):
        if update.channel_post.text == '/start':
            self.dialogue_point = 'start'
            self.username = ''
            self.user_phone = ''
            self.current_handler = None
            self.send_greeting_invitation(update, context)
            return

        self.current_handler(update, context)

    def handle_bot_button(self, update, context):
        # Обязательная команда (см. https://core.telegram.org/bots/api#callbackquery)
        update.callback_query.answer()
        self.current_handler(update, context)

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
        self.current_handler = self.handle_personal_data_processing_consent
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=question, reply_markup=reply_markup)

    def handle_personal_data_processing_consent(self, update, context):
        query = update.callback_query
        variant = query.data
        if variant == 'нет':
            return

        self.publish_consent_pdf
        message_start = f'Согласны?\n'
        self.send_username_input_invitation(update, context, message_start)

    def publish_consent_pdf(self, update, context):
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
        self.current_handler = self.handle_username_input
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    def handle_username_input(self, update, context):
        username = update.channel_post.text
        is_good_username = bool(username)
        if is_good_username:
            usernames = [sanitize_filename(name.strip()).capitalize() for name in username.split()]
            username = ' '.join(usernames)
            is_good_username = len(username) > 2

        if not is_good_username:
            self.send_username_input_invitation(update, context, message_start='Неправильное имя.\n')

        self.username = username
        self.send_user_phone_provision_way_invitation(update, context)

    def send_user_phone_provision_way_invitation(self, update, context):
        question = ('Телефон вы можете ввести вручную\n'
                    'или можете разрешить нам взять его из вашего Telegram.\n'
                    'Что выбираете?'
        ) 
        keyboard = [
             [
                 InlineKeyboardButton('Введу вручную', callback_data='введу'),
                 InlineKeyboardButton('Разрешаю взять', callback_data='разрешаю'),
             ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.current_handler = self.handle_user_phone_provision_way
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=question, reply_markup=reply_markup)

    def handle_user_phone_provision_way(self, update, context):
        query = update.callback_query
        variant = query.data
        if variant == 'введу':
            self.send_user_phone_input_invitation(update, context)

        self.get_user_phone_from_telegram(update, context)

    def send_user_phone_input_invitation(self, update, context, message_start=''):
        message = f'{message_start}Введите ваш телефон:'
        self.current_handler = self.handle_user_phone_input
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    def handle_user_phone_input(self, update, context):
        pass

    def get_user_phone_from_telegram(self, update, context):
        pass
       