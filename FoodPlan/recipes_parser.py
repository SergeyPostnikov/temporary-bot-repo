from recipe_bot.models import Category, Recipe

import requests
from bs4 import BeautifulSoup as bs


URL = 'https://www.edimdoma.ru/retsepty/?tags%5Brecipe_nutrition_type%5D%5B%5D='
HEADERS = {
    'access-control-expose-headers': 'AMP-Access-Control-Allow-Source-Origin',
    'amp-access-control-allow-source-origin': '<source-origin>',
    'cache-control': 'no-cache',
    'content-encoding': 'gzip',
    'content-type': 'text/html; charset=utf-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 '
                  'Safari/537.36'
}


def load_recipes_to_db():
    """Загружает рецепты с сайта edimdoma.ru в базу данных."""

    categories = ['Правильное питание', 'Низкокалорийные',
                  'Веганские', 'Детское меню']
    nutrition_types = [
        'правильное+питание+%28пп-рецепты%29',
        'низкокалорийные+рецепты',
        'веганские+рецепты',
        'детское+меню',
    ]
    recipes_titles = []
    for category_index, category_name in enumerate(categories):
        url = f'{URL}{nutrition_types[category_index]}'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        page_soup = bs(response.text, 'lxml')
        soup_pages_count = int(page_soup.find_all('a', class_='paginator__item false')[-1].text)
        page_number = 1
        while True:
            page_recipes = extract_recipes_from_page_soup(page_soup)
            for recipe in page_recipes:
                if recipe['title'] in recipes_titles:
                    continue
                recipes_titles.append(recipe['title'])
                recipe['description'], recipe['ingredients'] = (
                    get_description_and_ingredients(recipe['details_url'])
                )
                recipe['category_name'] = category_name
                try:
                    save_recipe_in_db(recipe)
                except:
                    continue
            page_number += 1
            if page_number > soup_pages_count:
                break
            page_url = f'{url}&page={page_number}'
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()
            page_soup = bs(response.text, 'lxml')

        print(len(recipes_titles))


def extract_recipes_from_page_soup(page_soup):
    """Забирает информацию о рецепт с одной html-страницы с перечнем рецептов."""

    page_recipes = []
    soup_recipes = page_soup.find_all('article', class_='card')
    for soup_recipe in soup_recipes:
        recipe = get_recipe_from_soup(soup_recipe)
        if (not recipe or
                not recipe['title'] or
                not recipe['picture']):
            continue
        page_recipes.append(recipe)
    return page_recipes


def get_recipe_from_soup(soup_recipe):
    """Вытаскивает информацию о рецепте из BeautifulSoup-объекта."""

    recipe = {}
    title = soup_recipe.find('div', 'title')
    try:
        recipe['title'] = title.text.strip()
        picture = soup_recipe.picture.img['src']
        picture_url, _ = picture.split('?')
        recipe['picture'] = picture_url
        recipe['details_url'] = f"https://www.edimdoma.ru{soup_recipe.a['href']}"
    except AttributeError:
        return None
    return recipe


def get_description_and_ingredients(details_url):
    """Вытаскивает ингредиенты и способ приготовления блюда по указанному url."""

    ingredients_response = requests.get(details_url, headers=HEADERS)
    ingredients_response.raise_for_status()

    soup = bs(ingredients_response.text, 'lxml')
    recipe_ingredients = soup.find_all(
        'input',
        class_='checkbox__input recipe_ingredient_checkbox'
    )
    ingredients = ''
    for ingredient in recipe_ingredients:
        title = ingredient['data-intredient-title']
        count = ingredient['data-amount']
        count_name = ingredient['data-unit-title']
        ingredients += f"{title} {count} {count_name}\n"

    descriptions_soup = soup.find_all(
        'div',
        class_='plain-text recipe_step_text'
    )
    description = ""
    for count, d in enumerate(descriptions_soup):
        description += '\n' + f'{count+1}. {d.get_text()} '
    return description, ingredients


def save_recipe_in_db(recipe):
    """Сохраняет рецепт в базе данных."""

    Category.objects.get_or_create(name=recipe['category_name'])
    category = Category.objects.get(name=recipe['category_name'])
    Recipe.objects.create(title=recipe['title'],
                          category=category, 
                          picture=recipe['picture'],
                          description=recipe['description'],
                          ingredients=recipe['ingredients'])
