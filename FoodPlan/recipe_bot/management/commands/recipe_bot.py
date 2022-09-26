import datetime
import logging
import time

import phonenumbers
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path
from pathvalidate import sanitize_filename
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.error import NetworkError
from telegram.ext import CallbackContext, CallbackQueryHandler, Filters
from telegram.ext import MessageHandler, Updater

from ...models import Category, Chat, Recipe


logger = logging.getLogger(__file__)


APP_NAME = 'recipe_bot'
START_STAGE = 0
CONSENT_PERSONAL_DATA_STAGE = 1
USERNAME_INPUT_STAGE = 2
PHONE_SENDING_STAGE = 3
MAIN_MENU_STAGE = 4
RECIPE_CATEGORY_MENU_STAGE = 5


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def __init__(self):
        super().__init__()
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            filename='recipe_bot.log',
            filemode='w'
        )
        self.updater = Updater(token=settings.TELEGRAM_BOT_TOKEN)
        bot_text_handler = MessageHandler(Filters.text | Filters.command,
                                          self.handle_bot_text)
        self.updater.dispatcher.add_handler(bot_text_handler)
        bot_button_handler = CallbackQueryHandler(self.handle_bot_button)
        self.updater.dispatcher.add_handler(bot_button_handler)
        bot_contact_handler = MessageHandler(Filters.contact,
                                             self.handle_phone_from_contacts)
        self.updater.dispatcher.add_handler(bot_contact_handler)
        self.handlers = {
            START_STAGE: self.send_greeting_invitation,
            CONSENT_PERSONAL_DATA_STAGE: self.handle_consent_personal_data,
            USERNAME_INPUT_STAGE: self.handle_username_input,
            PHONE_SENDING_STAGE: self.handle_phone_sending,
            MAIN_MENU_STAGE: self.handle_main_menu,
            RECIPE_CATEGORY_MENU_STAGE: self.handle_recipe_category_menu
        }

    def handle(self, *args, **kwargs):
        self.updater.start_polling()
        self.updater.idle()

    def handle_bot_text(self, update: Update, context: CallbackContext):
        chat_details = self.get_chat_details_from_db(update)
        dialogue_stage = chat_details['dialogue_stage']
        if (
            update.message.text == '/start' and
            dialogue_stage != START_STAGE
        ):
            dialogue_stage = self.update_dialogue_stage_in_db(
                update,
                START_STAGE
            )
        self.handlers[dialogue_stage](update, context)

    def handle_bot_button(self, update: Update, context: CallbackContext):
        # Обязательная команда
        # (см. https://core.telegram.org/bots/api#callbackquery)
        update.callback_query.answer()
        chat_details = self.get_chat_details_from_db(update)
        dialogue_stage = chat_details['dialogue_stage']
        self.handlers[dialogue_stage](update, context)

    def get_chat_details_from_db(self, update: Update) -> dict:
        chat_id = self.get_chat_id_from_bot(update)
        try:
            chat_details = Chat.get_chat_details(chat_id=chat_id)
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f'chat_id: {chat_id}')
        if chat_details is None:
            self.get_or_create_chat_in_db(update)
            chat_details = Chat.get_chat_details(chat_id=chat_id)
        return chat_details

    def update_dialogue_stage_in_db(self, update: Update,
                                    dialogue_stage: int) -> int:
        chat_id = self.get_chat_id_from_bot(update)
        dialogue_stage_from_db = Chat.update_dialogue_stage(
            chat_id=chat_id,
            dialogue_stage=dialogue_stage
        )
        if dialogue_stage_from_db is None:
            dialogue_stage_from_db = self.get_or_create_chat_in_db(update)

        if dialogue_stage_from_db != dialogue_stage:
            dialogue_stage_from_db = Chat.update_dialogue_stage(
                chat_id=chat_id,
                dialogue_stage=dialogue_stage
            )
        return dialogue_stage_from_db

    @staticmethod
    def get_chat_id_from_bot(update: Update) -> str:
        try:
            chat_id = update.message.chat.id
            return chat_id
        except AttributeError:
            chat_id = update.callback_query.message.chat.id
            return chat_id

    def get_or_create_chat_in_db(self, update: Update) -> int:
        chat_id = self.get_chat_id_from_bot(update)
        Chat.get_or_create_chat(chat_id)
        dialogue_stage_from_db = 0
        return dialogue_stage_from_db

    def send_greeting_invitation(self, update: Update,
                                 context: CallbackContext):
        chat_details = self.get_chat_details_from_db(update)
        if chat_details['username'] and chat_details['phone_number']:
            self.send_main_menu(update, context)
            return

        message = ('Давайте познакомимся.\n'
                   'Я хочу настроить свои предложения индивидуально для вас.\n'
                   'Для этого мне будут нужны ваше имя и телефон.\n'
                   'Вот наше Соглашение об обработке персональных данных:')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message)
        keyboard = [
            [
                InlineKeyboardButton('Согласен', callback_data='agree'),
                InlineKeyboardButton('Не согласен', callback_data='disagree'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.send_consent_pdf_to_chat(
            update,
            context,
            reply_markup=reply_markup
        )

    def send_consent_pdf_to_chat(self, update: Update,
                                 context: CallbackContext,
                                 reply_markup: InlineKeyboardMarkup = None):
        consent_pdf_filename = 'Consent_Of_Personal_Data_Processing.pdf'
        app_dirpath = apps.get_app_config(APP_NAME).path
        static_subfolder = settings.STATIC_URL.strip('/')
        pdf_subfolder = 'pdf'
        consent_pdf_filepath = (
            Path(app_dirpath) /
            static_subfolder /
            pdf_subfolder /
            consent_pdf_filename
        )
        self.update_dialogue_stage_in_db(update, CONSENT_PERSONAL_DATA_STAGE)
        self.send_file_to_chat(update, context, consent_pdf_filepath,
                               reply_markup)

    @staticmethod
    def send_file_to_chat(update: Update, context: CallbackContext,
                          filepath: Path,
                          reply_markup: InlineKeyboardMarkup = None):
        delay = 1
        while True:
            try:
                with open(filepath, 'rb') as file:
                    context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        reply_markup=reply_markup
                    )
                return
            except FileNotFoundError as ex:
                logger.warning(ex)
                logger.warning(f'Нет файла {filepath}')
                return
            except NetworkError as ex:
                logger.warning(ex)
                time.sleep(delay)
                delay = 10
            except Exception as ex:
                logger.warning(ex)
                return

    def handle_consent_personal_data(self, update: Update,
                                     context: CallbackContext):
        query = update.callback_query
        variant = query.data
        if variant != 'agree':
            return
        self.send_username_input_invitation(update, context)

    def send_username_input_invitation(self, update: Update,
                                       context: CallbackContext,
                                       message_start: str = ''):
        chat_details = self.get_chat_details_from_db(update)
        if chat_details['username']:
            self.send_phone_sending_invitation(update, context)
            return

        message = f'{message_start}Введите ваше имя:'
        self.update_dialogue_stage_in_db(update, USERNAME_INPUT_STAGE)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message)

    def handle_username_input(self, update: Update, context: CallbackContext):
        username = update.message.text.strip()
        is_good_username = bool(username)
        if is_good_username:
            usernames = [
                sanitize_filename(name.strip()).capitalize()
                for name in username.split()
            ]
            username = ' '.join(usernames)
            is_good_username = len(username) > 2

        if not is_good_username:
            self.send_username_input_invitation(
                update,
                context,
                message_start='Неправильное имя.\n'
            )
            return
        chat_id = self.get_chat_id_from_bot(update)
        Chat.update_username(chat_id=chat_id, username=username)
        self.send_phone_sending_invitation(update, context)

    def send_phone_sending_invitation(self, update: Update,
                                      context: CallbackContext,
                                      message_start: str = ''):
        chat_details = self.get_chat_details_from_db(update)
        if chat_details['phone_number']:
            self.send_main_menu(update, context)
            return

        message = (f'{message_start}'
                   'Введите номер телефона или нажмите кнопку, '
                   'чтобы отправить телефон автоматически')
        keyboard = [
            [
                KeyboardButton('Отправить телефон', callback_data='phone',
                               request_contact=True),
            ],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                           one_time_keyboard=True)
        self.update_dialogue_stage_in_db(update, PHONE_SENDING_STAGE)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message, reply_markup=reply_markup)

    def handle_phone_sending(self, update: Update, context: CallbackContext):
        phone_number = update.message.text.strip()
        phone_number = self.check_phone_number(phone_number)
        if not phone_number:
            self.send_phone_sending_invitation(
                update,
                context,
                message_start='Неправильный телефон.\n'
            )
            return
        self.save_phone_number_in_database(update, phone_number)
        self.send_main_menu(update, context)

    def handle_phone_from_contacts(self, update: Update,
                                   context: CallbackContext):
        contact = update.effective_message.contact
        phone_number = contact.phone_number
        phone_number = self.check_phone_number(phone_number)
        if not phone_number:
            self.send_phone_sending_invitation(
                update,
                context,
                message_start='Неправильный телефон.\n'
            )
            return
        self.save_phone_number_in_database(update, phone_number)
        self.send_main_menu(update, context)

    @staticmethod
    def check_phone_number(phone_number: str) -> str:
        try:
            phone_number = phonenumbers.parse(phone_number, 'RU')
            if phonenumbers.is_valid_number(phone_number):
                phone_number = phonenumbers.format_number(
                    phone_number,
                    phonenumbers.PhoneNumberFormat.E164
                )
            else:
                phone_number = ''
        except phonenumbers.NumberParseException:
            phone_number = ''
        return phone_number

    def save_phone_number_in_database(self, update: Update,
                                      phone_number: str):
        chat_id = self.get_chat_id_from_bot(update)
        Chat.update_phone_number(chat_id=chat_id, phone_number=phone_number)

    def send_main_menu(self, update: Update, context: CallbackContext,
                       text: str = '', keyboard_start: list = None):
        keyboard = [] if keyboard_start is None else keyboard_start
        chat_id = self.get_chat_id_from_bot(update)
        chat = Chat.objects.get(chat_id=chat_id)
        if chat.chat_date == datetime.date.today() and chat.recipes_count >= 3:
            message = text + '\n\n' if text else ''
            message = (f'{message}Вы уже просмотрели все 3 сегодняшних рецепта.\n'
                       'Новые рецепты будут доступны вам завтра.')
        else:
            message = text
            keyboard.append(
                [
                    InlineKeyboardButton('Показать рецепт', callback_data='recipe'),
                    InlineKeyboardButton('Выбрать категорию рецепта', callback_data='category'),
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton('Личный кабинет', callback_data='private'),
            ]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        if not message:
            message = 'Выберите:'        
        self.update_dialogue_stage_in_db(update, MAIN_MENU_STAGE)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message, reply_markup=reply_markup,
                                 parse_mode='Markdown')

    def handle_main_menu(self, update: Update, context: CallbackContext):
        query = update.callback_query
        variant = query.data
        methods = {
            'like': self.update_like_in_db,
            'dislike': self.update_dislike_in_db,
            'recipe': self.publish_recipe_in_chat,
            'category': self.send_recipe_category_menu,
            'private': self.open_private_office,
        }
        methods[variant](update, context)

    def publish_recipe_in_chat(self, update: Update,
                               context: CallbackContext):
        chat_id = self.get_chat_id_from_bot(update)
        recipe = Recipe.get_random_recipe(chat_id)
        Chat.update_recipe_id(chat_id, recipe.id)

        context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=recipe.picture,
                               caption=f'\n\n*{recipe.title}*\n\n',
                               parse_mode='Markdown')

        recipe_text = ('_Ингредиенты_\n\n'
                       f'{recipe.ingredients}\n'
                       '_Способ приготовления_\n'
                       f'{recipe.description}')
        
        keyboard = [
            [
                InlineKeyboardButton('👍', callback_data='like'),
                InlineKeyboardButton('👎', callback_data='dislike'),
            ],
        ]
        self.send_main_menu(update, context, text=recipe_text, keyboard_start=keyboard)

    def send_recipe_category_menu(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id_from_bot(update)
        chat_recipe_category_name = Chat.get_chat_recipe_category_name(chat_id=chat_id)
        if chat_recipe_category_name:
            text = (f'Выбрана категория рецептов: {chat_recipe_category_name}\n'
                    'Можете выбрать другую категорию:')
        else:
            text = ('Категория рецептов пока не выбрана\n'
                    'Выберите категорию:')

        all_recipe_categories = Category.get_all_categories_names()
        all_recipe_categories.append('Все')
        keyboard = []
        for category_index, category_name in enumerate(all_recipe_categories):
            if not category_index % 2:
                keyboard.append([])
            keyboard[-1].append(InlineKeyboardButton(category_name,
                                                     callback_data=category_name))

        reply_markup = InlineKeyboardMarkup(keyboard)
        self.update_dialogue_stage_in_db(update, RECIPE_CATEGORY_MENU_STAGE)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text, reply_markup=reply_markup)

    def handle_recipe_category_menu(self, update: Update, context: CallbackContext):
        query = update.callback_query
        category_name = query.data
        text = f'Выбрана категория рецептов: {category_name}'
        if category_name == 'Все':
            category_name = ''
        chat_id = self.get_chat_id_from_bot(update)
        Chat.update_recipe_category_name(chat_id=chat_id, category_name=category_name)
        self.send_main_menu(update, context, text=text)

    def update_like_in_db(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id_from_bot(update)
        Chat.add_recipe_like(chat_id=chat_id)
        self.send_main_menu(update, context)

    def update_dislike_in_db(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id_from_bot(update)
        Chat.add_recipe_dislike(chat_id=chat_id)
        self.send_main_menu(update, context)

    def open_private_office(self, update: Update, context: CallbackContext):
        chat_id = self.get_chat_id_from_bot(update)
        like_recipes_titles = Chat.get_like_recipes_titles(chat_id=chat_id)
        if like_recipes_titles:
            text = '\n'.join(['_Вам понравились эти рецепты:_\n'] + like_recipes_titles)
        else:
            text = 'Пока здесь ничего нет. Вы не лайкнули ни одного рецепта'
        self.send_main_menu(update, context, text=text)
