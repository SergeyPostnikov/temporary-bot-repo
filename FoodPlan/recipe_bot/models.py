import random
import datetime

from django.db import models


class Category(models.Model):
    """Категория рецепта."""

    name = models.CharField('Наименование категории рецепта', max_length=120,
                            db_index=True, null=False, blank=False)

    @classmethod
    def get_all_categories_names(cls):
        categories = cls.objects.all()
        return [category.name for category in categories]

    def __repr__(self):
        return self.name


class Chat(models.Model):
    """Чат в Telegram'е."""

    chat_id = models.CharField('Id чата с пользователем', max_length=64,
                               db_index=True, null=False, blank=False)
    username = models.CharField('Имя пользователя',
                                max_length=128, null=False, blank=True)
    phone_number = models.CharField('Номер телефона пользователя',
                                    max_length=16, default='',
                                    null=False, blank=True)
    dialogue_stage = models.IntegerField('Этап диалога пользователя с ботом',
                                         default=0)
    category_name = models.CharField('Выбранная категория рецептов', max_length=120,
                                null=False, blank=True, default='')
    recipe_id = models.IntegerField('Просматриваемый рецепт', default=-1,
                                    null=False, blank=True)
    chat_date = models.DateField('Дата диалога с пользователем',
                                 auto_now=True)
    recipes_count = models.IntegerField(
        'Количество показанных в дату диалога рецептов',
        default=0
    )

    @classmethod
    def get_or_create_chat(cls, chat_id, username=''):
        """Создаёт в БД чат, если он не был создан ранее."""
        return cls.objects.get_or_create(chat_id=chat_id, username=username)

    @classmethod
    def add_recipe_dislike(cls, chat_id):
        """Cтавит дизлайк рецепту c recipe_id из указанного чата."""

        chat = Chat.objects.get(chat_id=chat_id)
        if chat.recipe_id != -1:
            recipe = Recipe.objects.get(id=chat.recipe_id)
            chat.dislikes.add(recipe)

    @classmethod
    def add_recipe_like(cls, chat_id):
        """Ставит лайк рецепту c recipe_id из указанного чата."""

        chat = Chat.objects.get(chat_id=chat_id)
        if chat.recipe_id != -1:
            recipe = Recipe.objects.get(id=chat.recipe_id)
            chat.likes.add(recipe)

    @classmethod
    def get_chat_details(cls, chat_id):
        """Получает из БД имя пользователя, телефон
           и стадию диалога для чата."""

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
    def get_chat_recipe_category_name(cls, chat_id):
        """Получает из БД выбранную категорию рецептов для чата."""

        chats = cls.objects.filter(chat_id=chat_id).values('category_name')
        if len(chats) != 1:
            return None
        return chats[0]['category_name']

    @classmethod
    def get_like_recipes_titles(cls, chat_id):
        """Получает из БД заголовки лайккнутых в чате рецептов."""

        chat_likes = (cls.objects.get(chat_id=chat_id).likes.all()
                                 .values('title'))
        titles = sorted([recipe['title'] for recipe in chat_likes.iterator()])
        return [f'{title_number}. {title}'
                for title_number, title in enumerate(titles, 1)]

    @classmethod
    def update_dialogue_stage(cls, chat_id, dialogue_stage):
        """Изменяет стадию диалога для чата."""

        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        (cls.objects.filter(chat_id=chat_id)
                    .update(dialogue_stage=dialogue_stage))
        return dialogue_stage

    @classmethod
    def update_phone_number(cls, chat_id, phone_number):
        """Изменяет телефон пользователя чата."""

        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(phone_number=phone_number)
        return phone_number

    @classmethod
    def update_recipe_category_name(cls, chat_id, category_name):
        """Изменяет выбранную категорию рецептов для чата."""

        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(category_name=category_name)
        return category_name

    @classmethod
    def update_recipe_id(cls, chat_id, recipe_id):
        """Изменяет id выбранной в чате категории рецепта."""

        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(recipe_id=recipe_id)
        return recipe_id

    @classmethod
    def update_username(cls, chat_id, username):
        """Изменяет имя пользователя чата."""

        if cls.objects.filter(chat_id=chat_id).count() != 1:
            return None
        cls.objects.filter(chat_id=chat_id).update(username=username)
        return username

    def __repr__(self):
        return self.username


class Recipe(models.Model):
    """Рецепт блюда."""

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
    # categories = models.CharField(max_length=255, default='')

    def __repr__(self):
        return self.title

    @classmethod
    def get_random_recipe(cls, chat_id):
        """Возвращает случайный обект Recipe."""

        chat = Chat.objects.get(chat_id=chat_id)
        category_name = chat.category_name
        dislike_recipes = chat.dislikes.all()
        if category_name:
            # recipes = (Recipe.objects.filter(categories=category)
            #                          .exclude(pk__in=dislike_recipes))
            recipes = (Recipe.objects.filter(category__name=category_name)
                                     .exclude(pk__in=dislike_recipes))
        else:
            recipes = Recipe.objects.exclude(pk__in=dislike_recipes)
        random_recipe = random.choice(recipes)
        if chat.chat_date != datetime.date.today():
            chat.chat_date = datetime.date.today()
            chat.recipes_count = 0
        chat.recipes_count += 1  # Счетчик показов рецептов у пользователя
        chat.chat_date = datetime.date.today()
        chat.save()
        return random_recipe
