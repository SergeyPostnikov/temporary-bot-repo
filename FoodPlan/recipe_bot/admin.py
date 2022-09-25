from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Chat, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'chat_id', 'category')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'picture', 'description', 'ingredients')
    list_display_links = ('title', 'description')
    raw_id_fields = ('category',)
