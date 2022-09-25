# import phonenumbers
import random

from django.db import models
from django.db.models import Q
# from phonenumber_field.modelfields import PhoneNumberField


class Category(models.Model):
    """Категория рецепта"""

    name = models.CharField('Наименование категории рецепта', max_length=120,
                            db_index=True, null=False, blank=False)

    @classmethod
    def get_all_categories_names(cls):
        categories = cls.objects.all()
        return [category.name for category in categories]

    def __repr__(self):
        return self.name

class Chat(models.Model):
    """Чат в Telegram'е"""

    chat_id = models.CharField('Id чата с пользователем', max_length=64, 
                               db_index=True, null=False, blank=False)
    username = models.CharField('Имя пользователя',
                                max_length=128, null=False, blank=True)
    phone_number = models.CharField('Номер телефона пользователя', max_length=16, 
                                    default='', null=False, blank=True)
    dialogue_stage = models.IntegerField('Этап диалога пользователя с ботом', default=0)
    category = models.CharField('Выбранная категория рецептов', max_length=120, 
                                null=False, blank=True, default='')
    recipe_id = models.IntegerField('Просматриваемый рецепт', default=-1,
                                    null=False, blank=True)

    @classmethod
    def get_or_create_chat(cls, chat_id, username=''):
        return cls.objects.get_or_create(chat_id=chat_id, username=username)

    @classmethod
    def get_chat_details(cls, chat_id):
        chats = cls.objects.filter(chat_id=chat_id)
        if len(chats) != 1:
            return None

        chat_details = {
            'chat_id': chat_id,
            'username': chats[0].username,
            'phone_number': chats[0].phone_number,            
            'dialogue_stage': chats[0].dialogue_stage,
        }
        return chat_details

    @classmethod
    def get_like_recipes_titles(cls, chat_id):
        chat_likes = cls.objects.get(chat_id=chat_id).likes.all().values('title')
        titles = sorted([recipe['title'] for recipe in chat_likes.iterator()])
        return [f'{title_number}. {title}' for title_number, title in enumerate(titles, 1)]

    @classmethod
    def get_chat_recipe_category(cls, chat_id):
        chats = cls.objects.filter(chat_id=chat_id).values('category')
        if len(chats) != 1:
            return None
        return chats[0]['category']

    @classmethod
    def update_dialogue_stage(cls, chat_id, dialogue_stage):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(dialogue_stage=dialogue_stage)
        return dialogue_stage

    @classmethod
    def update_recipe_id(cls, chat_id, recipe_id):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(recipe_id=recipe_id)
        return recipe_id

    @classmethod
    def update_recipe_category(cls, chat_id, category):
        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(category=category)
        return category

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
    def add_recipe_like(cls, chat_id):
        """Поставить лайк рецепту c recipe_id из указанного чата"""

        chat = Chat.objects.get(chat_id=chat_id)
        recipe = Recipe.objects.get(id=chat.recipe_id)
        chat.likes.add(recipe)

    @classmethod
    def add_recipe_dislike(cls, chat_id):
        """Поставить дизлайк рецепту c recipe_id из указанного чата"""

        chat = Chat.objects.get(chat_id=chat_id)
        recipe = Recipe.objects.get(id=chat.recipe_id)
        chat.dislikes.add(recipe)

    def __repr__(self):
        return self.username


class Recipe(models.Model):
    """Рецепт блюда"""

    picture = models.CharField(max_length=255, default='')
    title = models.CharField(max_length=255, default='')
    ingredients = models.TextField(max_length=400, default='')
    description = models.TextField(max_length=1000, default='a', null=True)
    like = models.ManyToManyField(Chat, related_name='likes')
    dislike = models.ManyToManyField(Chat, related_name='dislikes')
    category = models.ForeignKey(
        Category,
        related_name='recipes',
        verbose_name='Категория рецепта',
        on_delete=models.PROTECT
    )
    categories = models.CharField(max_length=255, default='')

    def __repr__(self):
        return self.title

    def get_recipe(cls, user):
        pref = user.preferences
        recipes = cls.objects.filter(category__in=pref)
        return recipes

    @classmethod
    def get_random_recipe(cls, chat_id):
        """Возвращает рандомный обект Recipe, обращаться через точку .title ... .picture .... .description"""

        chat = Chat.objects.get(chat_id=chat_id)
        category = chat.category
        dislike_recipes = chat.dislikes.all()
        if category:
            recipes = Recipe.objects.filter(categories=category).exclude(pk__in=dislike_recipes)
        else:
            recipes = Recipe.objects.exclude(pk__in=dislike_recipes)
        random_recipe = random.choice(recipes)
        return random_recipe

    @classmethod
    def get_all_random_category(cls):
        "Возвращает QuerySet, рандомных категорий которые есть в БД"

        return cls.objects.all().values('category').distinct()

