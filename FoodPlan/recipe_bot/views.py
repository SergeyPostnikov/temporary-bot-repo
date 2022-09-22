from django.shortcuts import render
from .models import User, Recipe
from random import rand


def create_user_wrapper():
    '''можно удалять wrapper
    т.к. это оболочка для демо'''
    return User.create_user('Steve Jobs', phone_number='6666336626')


def get_recipe_wrapper(user):
    '''можно удалять wrapper
    т.к. это оболочка для демо
    функция принимает объект типа User
    функция возвращает QuerySet(т.е. функция недопилена)'''
    return Recipe.get_recipe(user)

