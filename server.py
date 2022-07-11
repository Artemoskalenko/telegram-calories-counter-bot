import logging
import os

from aiogram import Bot, Dispatcher, executor, types

from dishes import Dishes
import exceptions
import meals
from middlewares import AccessMiddleware


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для учёта калорий\n\n"
        "Добавить приём пищи: 100 филе куриное\n"
        "Сегодняшняя статистика: /meals\n"
        "Сколько осталось съесть сегодня: /rest\n"
        "Категории блюд: /dishes")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о приёме пищи по её идентификатору"""
    row_id = int(message.text[4:])
    meals.delete_meal(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['rest'])
async def get_rest(message: types.Message):
    """Отображает сколько осталось съесть сегодня"""
    answer_message = (
        f"{meals.get_today_rest()}")
    await message.answer(answer_message)


@dp.message_handler(commands=['dishes'])
async def dishes_list(message: types.Message):
    """Отправляет список категорий блюд"""
    dishes = Dishes().get_all_dishes()
    answer_message = "Категории блюд:\n\n* " +\
        ("\n* ".join([d.name+' ('+", ".join(d.aliases)+')' for d in dishes]))
    await message.answer(answer_message)


@dp.message_handler(commands=['meals'])
async def today_meals(message: types.Message):
    """Отображает сегодняшние перекусы"""
    meals_list = meals.last()
    if not meals_list:
        await message.answer("Сегодня вы еще не ели")
        return

    meals_list_rows = [
        f"{meal.weight} гр. {meal.dish_name} — нажми "
        f"/del{meal.id} для удаления"
        for meal in meals_list]
    answer_message = "Последние приёмы пищи:\n\n* " + "\n\n* ".join(meals_list_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_meal(message: types.Message):
    """Добавляет новый приём пищи"""
    try:
        meal = meals.add_meal(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлено {meal.weight} гр {meal.dish_name}.\n\n"
        f"{meals.get_today_rest()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)