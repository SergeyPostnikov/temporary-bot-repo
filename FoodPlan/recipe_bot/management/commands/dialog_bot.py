import collections
import logging

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyMarkup
from telegram.ext import Updater

from .bot_items import Message


logger = logging.getLogger(__file__)


class DialogBot(object):

    def __init__(self, token, generator, handlers=None):
        self.updater = Updater(token=token)
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(generator, handlers or {})

    def start(self):
        self.updater.start_polling()

    def handle_message(self, update, callback_context):
        chat_id = update.channel_post.chat.id
        if update.channel_post.text == "/start":
            self.handlers.pop(chat_id, None)

        if chat_id not in self.handlers:
            answer = next(self.handlers[chat_id])
        else:
            try:
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                del self.handlers[chat_id]
                return self.handle_message(bot, update)
        self._send_answer(callback_context.bot, chat_id, answer)

    def _send_answer(self, bot, chat_id, answer):
        logger.warning(f'Sending answer {answer} to {chat_id}')
        is_only_one_answer = isinstance(answer, str) or not isinstance(answer, collections.abc.Iterable)
        if  is_only_one_answer:
            answer = [self._convert_answer_part(answer)]
        else:
            answer = list(map(self._convert_answer_part, answer))

        current_message = None
        for part in answer:
            if isinstance(part, Message):
                if current_message is not None:
                    options = dict(current_message.options)
                    options.setdefault('disable_notification', True)
                    bot.sendMessage(chat_id=chat_id, text=current_message.text, **options)
                current_message = part
            if isinstance(part, ReplyMarkup):
                current_message.options['reply_markup'] = part

        if current_message is not None:
            bot.sendMessage(chat_id=chat_id, text=current_message.text, **current_message.options)

    def _convert_answer_part(self, answer_part):
        if isinstance(answer_part, str):
            return Message(answer_part)

        if isinstance(answer_part, collections.abc.Iterable):
            answer_part = list(answer_part)
            is_keyboard = isinstance(answer_part[0], str)
            if is_keyboard:
                return ReplyKeyboardMarkup([answer_part], one_time_keyboard=True)

            if isinstance(answer_part[0], collections.abc.Iterable):
                answer_part = list(map(list, answer_part))
                is_keyboard = isinstance(answer_part[0][0], str)
                if is_keyboard:
                    return ReplyKeyboardMarkup(answer_part, one_time_keyboard=True)
        return answer_part
