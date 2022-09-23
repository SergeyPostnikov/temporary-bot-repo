# import phonenumbers
from django.db import models
# from phonenumber_field.modelfields import PhoneNumberField


class Chat(models.Model):
    categories = (
        ('a', 'all'), 
        ('u', 'usual'), 
        ('v', 'vegeterian'), 
        ('k', 'for kids'))
    chat_id = models.CharField('Id чата с пользователем', max_length=64, 
                               db_index=True, null=False, blank=False)
    username = models.CharField('Username пользователя из Telegram',
                                max_length=32, null=False, blank=False)
    first_name = models.CharField('Имя пользователя',
                                  max_length=64, null=False, blank=False)
    last_name = models.CharField('Фамилия пользователя',
                                 max_length=64, null=False, blank=False)
    phone_number = models.CharField('Номер телефона', max_length=16, 
                                    default='', null=False, blank=True)
    # pure_phone = PhoneNumberField('Нормализованный номер телефона',
    #                               default='', null=False, blank=True)
    bot_status = models.IntegerField(default=0)
    preference = models.CharField(choices=categories, default='a', max_length=10)

    @classmethod
    def get_or_create_chat(cls, chat_id, username, first_name, last_name):
        return cls.objects.get_or_create(chat_id=chat_id, username=username, 
                                         first_name=first_name, last_name=last_name)

    # @classmethod
    # def normalize_phone_number(cls, phone_number):
    #     try:
    #         pure_phone = phonenumbers.parse(phone_number, 'RU')
    #     except phonenumbers.NumberParseException:
    #         pure_phone = ''

    #     if phonenumbers.is_valid_number(pure_phone):
    #         pure_phone = phonenumbers.format_number(
    #             pure_phone,
    #             phonenumbers.PhoneNumberFormat.E164
    #         )
    #     return pure_phone

    def __repr__(self):
        return self.username


class Recipe(models.Model):
    categories = (
        ('u', 'usual'), 
        ('v', 'vegeterian'), 
        ('k', 'for kids'))
    reactions = (
        ('l', 'like'), 
        ('d', 'dislike'), 
        ('i', 'indifferent'))
    picture = models.ImageField(upload_to=None)
    description = models.TextField(max_length=255)
    category = models.CharField(choices=categories, max_length=10)
    reaction = models.CharField(choices=reactions, max_length=10)
    chats = models.ManyToManyField(
        Chat,  
        related_name='recipes',
        blank=True)

    def __repr__(self):
        return self.description

    def get_ingredients(self):
        return self.ingredients.all()

    def get_recipe(cls, user):
        pref = user.preferences
        recipes = cls.objects.filter(category__in=pref)
        return recipes


class Ingredient(models.Model):
    name = models.CharField(max_length=255, blank=False)
    amount = models.FloatField(blank=False)
    measure = models.CharField(max_length=10, blank=False)
    recipe = models.ForeignKey(
        'Recipe', 
        related_name='ingredients', 
        on_delete=models.CASCADE)

    def __repr__(self):
        return self.name


# функционал модели
# регистрировать юзера
# регистрировать рецепт
# выдавать рецепт
# ставить лайк/dislike

if __name__ == '__main__':
    from recipe_bot.models import *
    user = User.create_user('Steve Jobs', phone_number='6666336626')

    potatoes = Recipe.objects.create(description='Жареная картошка')
    potato = Ingredient.objects.create(name='картошка', amount=4, recipe=potatoes, measure='шт')
    oil = Ingredient.objects.create(name='масло', amount=5, recipe=potatoes, measure='мл')
    salt = Ingredient.objects.create(name='соль', amount=1, recipe=potatoes, measure='ч.л.')

    print(potatoes.get_ingredients())