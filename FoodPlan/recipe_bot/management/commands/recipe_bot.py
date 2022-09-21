import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from .dialog_bot import DialogBot


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def __init__(self):
        pass
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO,
                            filename='recipe_bot.log',
                            filemode='w'
        )

    def handle(self, *args, **kwargs):
        dialog_bot = DialogBot(settings.TELEGRAM_BOT_TOKEN, self.bot_generator)
        dialog_bot.start()

    def bot_generator(self):
        answer = yield ('Рад встрече!\n'
                        'Я могу подбирать для вас рецепты блюд.\n'
                        'Заинтересовались?\n'
                        'Давайте познакомимся.\n'
                        'Как вас зовут?'
        )
