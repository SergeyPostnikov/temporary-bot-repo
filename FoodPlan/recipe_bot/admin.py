from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Chat, Recipe


@admin.register(Chat)  # Регистрируем модель категории с помошью декоратора
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'categories', 'phone_number', 'chat_id', 'likes')  # Отображение нужных нам столбцов в Админ, порядок как сдесь
    # list_display_links = ('name', 'categories')  # Указывается поле которое будет ссылкой на выбранную категорию
    raw_id_fields = ('likes', 'dislikes')

@admin.register(Recipe)  # Регистрируем модель категории с помошью декоратора
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'picture', 'description', 'category', 'ingredients', 'reaction')  # Отображение нужных нам столбцов в Админ, порядок как сдесь
    list_display_links = ('title', 'description')
    raw_id_fields = ('like', 'dislike')

# @admin.register(Ingredient)  # Регистрируем модель категории с помошью декоратора
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'amount', 'measure')  # Отображение нужных нам столбцов в Админ, порядок как сдесь

