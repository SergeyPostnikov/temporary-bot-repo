# import phonenumbers
import random

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
    username = models.CharField('Username пользователя',
                                max_length=128, null=False, blank=True)
    phone_number = models.CharField('Номер телефона пользователя', max_length=16, 
                                    default='', null=False, blank=True)
    dialogue_stage = models.IntegerField('Этап диалога с ботом', default=0)
    preference = models.CharField(choices=categories, default='a', max_length=10)

    @classmethod
    def get_or_create_chat(cls, chat_id, username=''):
        return cls.objects.get_or_create(chat_id=chat_id, username=username)

    @classmethod
    def get_chat_details(cls, chat_id):
        chats = cls.objects.filter(chat_id=chat_id)
        if not chats:
            return None

        chat_details = {
            'chat_id': chats[0].chat_id,
            'username': chats[0].username,
            'phone_number': chats[0].phone_number,            
            'dialogue_stage': chats[0].dialogue_stage,
        }
        return chat_details

    @classmethod
    def update_dialogue_stage(cls, chat_id, dialogue_stage):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(dialogue_stage=dialogue_stage)
        return dialogue_stage

    @classmethod
    def update_username(cls, chat_id, username):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(username=username)
        return username

    @classmethod
    def update_phone_number(cls, chat_id, phone_number):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(phone_number=phone_number)
        return phone_number

    @classmethod
    def add_likes_recipe(cls, chat_id, recipe):
        "Поставить лайк рецепту, параметрами передаются объкт Recipe и номер чата"

        chat = Chat.objects.get(chat_id=chat_id)
        chat.likes.add(recipe)

    @classmethod
    def add_dislikes_recipe(cls, chat_id, recipe):
        "Поставить дизлайк рецепту, параметрами передаются объкт Recipe и номер чата"

        chat = Chat.objects.get(chat_id=chat_id)
        chat.dislikes.add(recipe)

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
        ('k', 'for kids'),
        ('d', 'dietary'),
        ('a', 'vegan'))
    reactions = (
        ('l', 'like'), 
        ('d', 'dislike'), 
        ('i', 'indifferent'))
    picture = models.CharField(max_length=255, default='')
    title = models.CharField(max_length=255, default='')
    ingredients = models.TextField(max_length=400, default='')
    description = models.TextField(max_length=1000, default='a', null=True)
    category = models.CharField(choices=categories, max_length=10)
    reaction = models.CharField(choices=reactions, max_length=10, default='i')
    like = models.ManyToManyField(Chat, related_name='likes')
    dislike = models.ManyToManyField(Chat, related_name='dislikes')
    chats = models.ManyToManyField(
        Chat,  
        related_name='recipes',
        blank=True)

    def __repr__(self):
        return self.title

    # def get_ingredients(self):
    #     return self.ingredients.all()

    def get_recipe(cls, user):
        pref = user.preferences
        recipes = cls.objects.filter(category__in=pref)
        return recipes

    @classmethod
    def get_random_recipe(cls):
        "Возвращает рандомный обект Recipe, обращаться через точку .title ... .picture .... .description"

        recipes = cls.objects.all()
        random_recipe = random.choice(recipes)
        return random_recipe

    @classmethod
    def get_all_random_category(cls):
        "Возвращает QuerySet, рандомных категорий которые есть в БД"

        return cls.objects.all().values('category').distinct()

    # @classmethod
    # def add_likes_chat(cls, chat_id, recipe):
    #     "Поставить лайк рецепту, параметрами передаются объкт Recipe и номер чата"
    #
    #     chat = Chat.objects.get(chat_id=chat_id)
    #     recipe.like.add(chat)
    #
    # @classmethod
    # def add_dislikes_chat(cls, chat_id, recipe):
    #     "Поставить дизлайк рецепту, параметрами передаются объкт Recipe и номер чата"
    #
    #     chat = Chat.objects.get(chat_id=chat_id)
    #     recipe.dislike.add(chat)



# class Ingredient(models.Model):
#     name = models.CharField(max_length=255, blank=False)
#     amount = models.FloatField(blank=False)
#     measure = models.CharField(max_length=10, blank=False)
#     recipe = models.ForeignKey(
#         'Recipe',
#         related_name='ingredients',
#         on_delete=models.CASCADE)
#
#     def __repr__(self):
#         return self.name


# функционал модели
# регистрировать юзера
# регистрировать рецепт
# выдавать рецепт
# ставить лайк/dislike

# if __name__ == '__main__':
#     from recipe_bot.models import *
#     user = User.create_user('Steve Jobs', phone_number='6666336626')
#
#     potatoes = Recipe.objects.create(description='Жареная картошка')
#     potato = Ingredient.objects.create(name='картошка', amount=4, recipe=potatoes, measure='шт')
#     oil = Ingredient.objects.create(name='масло', amount=5, recipe=potatoes, measure='мл')
#     salt = Ingredient.objects.create(name='соль', amount=1, recipe=potatoes, measure='ч.л.')
#
#     print(potatoes.get_ingredients())