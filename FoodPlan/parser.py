from pprint import pprint

import requests
from bs4 import BeautifulSoup as b


URL = 'https://www.edimdoma.ru/retsepty/'
API_KEI = '5465780969:AAEbul6zfVI38kWCKxQjn9jta92NUm40KUE'
categories = ['вегетарианские рецепты', 'диабетические рецепты', 'веганские рецепты', 'детское меню']
recipes = []
headers = {
    'access-control-expose-headers': 'AMP-Access-Control-Allow-Source-Origin',
    'amp-access-control-allow-source-origin': '<source-origin>',
    'cache-control': 'no-cache',
    'content-encoding': 'gzip',
    'content-type': 'text/html; charset=utf-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}


def get_html(url, params=None):
    response = requests.get(url, headers=headers, params=params)
    return response


def get_soup(c):
    soup = b(c.text, 'lxml')
    return soup


def get_recipes(category, params):
    html_response = get_html(URL, params=params)
    soup_html = get_soup(html_response)
    try:
        soup_recipes = soup_html.find_all('article', class_='card')
    except AttributeError:
        pass
    for soup_recipe in soup_recipes:
        recipe = {}
        try:
            picture = soup_recipe.picture.img['src']
            picture_url, _ = picture.split('?')
            recipe['picture'] = picture_url
            title = soup_recipe.find('div', 'title')
            recipe['title'] = title.text
            url_details = f"https://www.edimdoma.ru{soup_recipe.a['href']}"
            response_ingredients = get_html(url_details, params=params)
        except TypeError:
            pass
        soup = get_soup(response_ingredients)
        recipe_ingredients = soup.find_all('input', class_='checkbox__input recipe_ingredient_checkbox')
        ingredients = []
        for ingredient in recipe_ingredients:
            title = ingredient['data-intredient-title']
            count = ingredient['data-amount']
            ingredients.append(f"{title} - {count}")
        recipe['ingredients'] = ingredients
        recipe['category'] = category
        if 'title' in recipe:
            recipes.append(recipe)
    return recipes


def get_recipes_by_categories():
    for category in categories:
        params = {
            'recipe_nutrition_type': category
        }
        recipes_by_categories = get_recipes(category, params)
    return recipes_by_categories


pprint(get_recipes_by_categories())