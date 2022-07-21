import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

import db
from dishes import Dishes, FSMDish
import exceptions
import meals
from middlewares import AccessMiddleware
from keyboards import keyboard


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        f"Бот для учёта калорий\n\n"
        f"Добавить приём пищи: 100 филе куриное\n"
        f"Сегодняшняя статистика: /meals\n"
        f"Сколько осталось съесть сегодня: /rest\n"
        f"Категории блюд: /dishes\n"
        f"Установить новый вес пользователя: /weight75\n"
        f"Добавить новое блюдо: /newdish", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.startswith('/weight'))
async def set_weight(message: types.Message):
    """Устанавливает новый вес пользователя"""
    user_weight = int(message.text[7:])
    db.update_weight(user_weight)
    answer_message = f"Установлен новый вес пользователя: {user_weight}\n\nСуточные нормы:\nкалории - {user_weight*33}\n" \
                     f"белки - {user_weight*2}\nжири - {user_weight}\nуглеводы - {user_weight*4}\n\n" \
                     f"Установить новый вес пользователя: /weight{db.get_weight()-1}\n" \
                     f"Установить новый вес пользователя: /weight{db.get_weight()+1}\n"
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_meal(message: types.Message):
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


@dp.message_handler(commands='newdish', state=None)
async def new_dish(message: types.Message):
    """Включение машины состояний для добавления нового блюда"""
    await FSMDish.codename.set()
    await message.reply("Введите кодовое название блюда (на английском)")


@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


@dp.message_handler(state=FSMDish.codename)
async def load_codename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['codename'] = message.text
    await FSMDish.next()
    await message.reply("Введите название блюда")


@dp.message_handler(state=FSMDish.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMDish.next()
    await message.reply("Введите количество калорий на 100гр. блюда")


@dp.message_handler(state=FSMDish.calories)
async def load_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['calories'] = float(message.text)
    await FSMDish.next()
    await message.reply("Введите количество белков на 100гр. блюда")


@dp.message_handler(state=FSMDish.proteins)
async def load_proteins(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['proteins'] = float(message.text)
    await FSMDish.next()
    await message.reply("Введите количество жиров на 100гр. блюда")


@dp.message_handler(state=FSMDish.fats)
async def load_fats(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fats'] = float(message.text)
    await FSMDish.next()
    await message.reply("Введите количество углеводов на 100гр. блюда")


@dp.message_handler(state=FSMDish.carbohydrates)
async def load_carbohydrates(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['carbohydrates'] = float(message.text)
    await FSMDish.next()
    await message.reply("Введите дополнительные названия блюда через запятую")


@dp.message_handler(state=FSMDish.aliases)
async def load_aliases(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['aliases'] = message.text

    await db.add_dish(state)
    await message.answer(f'Новое блюдо было добавлено в меню\n\n'
                         f'Посмотреть список блюд: /dishes')
    await state.finish()


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