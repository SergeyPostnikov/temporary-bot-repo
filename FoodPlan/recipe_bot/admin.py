from django.contrib import admin

from .models import Chat, Ingredient, Recipe

admin.site.register(Chat)
admin.site.register(Ingredient)
admin.site.register(Recipe)