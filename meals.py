import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from dishes import Dishes


class Message(NamedTuple):
    """Структура распаршенного сообщения о приёме пищи"""
    weight: int
    dish_text: str


class Meal(NamedTuple):
    """Структура добавленного в БД нового приёма пищи"""
    id: Optional[int]
    weight: int
    dish_name: str


def add_meal(raw_message: str) -> Meal:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    dish = Dishes().get_dish(parsed_message.dish_text)
    meal_calories = float((dish.calories * float(parsed_message.weight))/100.0)
    meal_proteins = float((dish.proteins * float(parsed_message.weight))/100.0)
    meal_fats = float((dish.fats * float(parsed_message.weight))/100.0)
    meal_carbohydrates = float((dish.carbohydrates * float(parsed_message.weight))/100.0)
    insert_row_id = db.insert("meal", {
        "weight": parsed_message.weight,
        "created": _get_now_formatted(),
        "dish_codename": dish.codename,
        "calories": meal_calories,
        "proteins": meal_proteins,
        "fats": meal_fats,
        "carbohydrates": meal_carbohydrates
    })
    return Meal(id=None,
                weight=parsed_message.weight,
                dish_name=dish.name)


def get_today_rest() -> str:
    """Возвращает строкой сколько осталось съесть за сегодня"""
    cursor = db.get_cursor()
    cursor.execute("select sum(calories)"
                   "from meal where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня вы еще ничего не ели"
    all_today_meals = result[0]
    cursor.execute("select sum(calories_limit) from info")
    result = cursor.fetchone()
    base_today_meals = result[0] if result[0] else 0
    rest = result[0] - all_today_meals
    if rest < 0:
        rest = 0
    return(f"Питание сегодня:\n"
           f"Всего — {int(all_today_meals)} калорий\n"
           f"Дневной лимит — {int(base_today_meals)} калорий\n"
           f"Сегодня осталось съесть — {int(rest)} калорий")


def last() -> List[Meal]:
    """Возвращает сегодняшние приёмы пищи"""
    cursor = db.get_cursor()
    cursor.execute(
        "select m.id, m.weight, d.name "
        "from meal m left join dish d "
        "on d.codename=m.dish_codename "
        "where date(created)=date('now', 'localtime')")
    rows = cursor.fetchall()
    last_meals = [Meal(id=row[0], weight=row[1], dish_name=row[2]) for row in rows]
    return last_meals


def delete_meal(row_id: int) -> None:
    """Удаляет приём пищи по его идентификатору"""
    db.delete("meal", row_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 курица")

    weight = regexp_result.group(1).replace(" ", "")
    dish_text = regexp_result.group(2).strip().lower()
    return Message(weight=weight, dish_text=dish_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Киев."""
    tz = pytz.timezone("Europe/Kiev")
    now = datetime.datetime.now(tz)
    return now


def _get_calories_limit() -> int:
    return db.fetchall("info", ["calories_limit"])[0]["calories_limit"]