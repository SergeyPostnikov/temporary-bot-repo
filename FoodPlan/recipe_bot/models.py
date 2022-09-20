from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)


class Recipe(models.Model):
    picture = models.field_name = models.ImageField(upload_to=None)
    description = models.TextField()


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    amount = models.FloatField()
    measure = models.CharField(max_length=10)
    recipe = models.ForeignKey(
        'Recipe', 
        related_name='ingredients', 
        on_delete=models.CASCADE)
