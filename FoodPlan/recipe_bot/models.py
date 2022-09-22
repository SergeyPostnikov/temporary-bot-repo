from django.db import models
from django.core.validators import RegexValidator


class User(models.Model):
    categories = (
        ('u', 'usual'), 
        ('v', 'vegeterian'), 
        ('k', 'for kids'))
    name = models.CharField(max_length=255, blank=False)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Неверный формат заиси номера")
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=False)
    preferences = models.CharField(choices=categories, max_length=10)

    @classmethod
    def create_user(cls, name, phone_number):
        return cls.objects.create(name=name, phone_number=phone_number)

    def __repr__(self):
        return self.name


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
    users = models.ManyToManyField(
        User,  
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
