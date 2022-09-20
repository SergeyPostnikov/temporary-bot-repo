from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)


class Recipe(models.Model):
    ingredients = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    picture = models.field_name = models.ImageField(upload_to=None)
    description = models.TextField()
    ingredients = models. #Поле для списка всех Ingredients


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    amount = models.FloatField()
    measure = models.CharField(max_length=10)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

