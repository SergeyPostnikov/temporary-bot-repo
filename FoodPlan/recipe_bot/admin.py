from django.contrib import admin

from .models import Category, Chat, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'chat_id', 'category_name',
                    'recipe_id', 'chat_date', 'recipes_count')
    raw_id_fields = ('likes', 'dislikes',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'picture', 'description', 'ingredients')
    list_display_links = ('title', 'description')
    raw_id_fields = ('category',)
