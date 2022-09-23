from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Chat, Recipe, Ingredient


@admin.register(Chat)  # Регистрируем модель категории с помошью декоратора
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'categories', 'phone_number', 'chat_id')  # Отображение нужных нам столбцов в Админ, порядок как сдесь
    # list_display_links = ('name', 'categories')  # Указывается поле которое будет ссылкой на выбранную категорию


@admin.register(Recipe)  # Регистрируем модель категории с помошью декоратора
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('picture', 'description', 'category', 'reaction')  # Отображение нужных нам столбцов в Админ, порядок как сдесь



@admin.register(Ingredient)  # Регистрируем модель категории с помошью декоратора
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'measure')  # Отображение нужных нам столбцов в Админ, порядок как сдесь