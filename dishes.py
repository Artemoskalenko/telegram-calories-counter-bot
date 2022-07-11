"""Работа с категориями блюд"""
from typing import Dict, List, NamedTuple

import db
import exceptions


class Dish(NamedTuple):
    """Структура категории блюда"""
    codename: str
    name: str
    calories: float
    proteins: float
    fats: float
    carbohydrates: float
    aliases: List[str]


class Dishes:
    def __init__(self):
        self._dishes = self._load_dishes()

    def _load_dishes(self) -> List[Dish]:
        """Возвращает справочник категорий блюд из БД"""
        dishes = db.fetchall(
            "dish", "codename name calories proteins fats carbohydrates aliases".split()
        )
        dishes = self._fill_aliases(dishes)
        return dishes

    def _fill_aliases(self, dishes: List[Dict]) -> List[Dish]:
        """Заполняет по каждой категории aliases, то есть возможные
        названия этой категории, которые можем писать в тексте сообщения.
        Например, категория «филе» может быть написана как курица,
        котлета и тд."""
        dishes_result = []
        for index, dish in enumerate(dishes):
            aliases = dish["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(dish["codename"])
            aliases.append(dish["name"])
            dishes_result.append(Dish(
                codename=dish['codename'],
                name=dish['name'],
                calories=dish['calories'],
                proteins=dish['proteins'],
                fats=dish['fats'],
                carbohydrates=dish['carbohydrates'],
                aliases=aliases
            ))
        return dishes_result

    def get_all_dishes(self) -> List[Dict]:
        """Возвращает справочник категорий."""
        return self._dishes

    def get_dish(self, dish_name: str) -> Dish:
        """Возвращает категорию блюда по одному из её алиасов."""
        finded = None
        for dish in self._dishes:
            for alias in dish.aliases:
                if dish_name in alias:
                    finded = dish
        if not finded:
            raise exceptions.NotCorrectMessage(
                "Неизвестное блюдо\n"
                "Чтобы просмотреть список блюд, введите /dishes")

        return finded
