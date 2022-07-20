from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import db

b1 = KeyboardButton('/start')
b8 = KeyboardButton('/help')
b2 = KeyboardButton('/rest')
b3 = KeyboardButton('/dishes')
b4 = KeyboardButton('/meals')
b5 = KeyboardButton(f'/weight{(db.get_weight()//10)*10}')
b6 = KeyboardButton(f'/weight{(db.get_weight()//10)*10+5}')
b7 = KeyboardButton(f'/weight{(db.get_weight()//10)*10+10}')

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

keyboard.row(b1).row(b2, b3, b4).row(b5, b6, b7)
