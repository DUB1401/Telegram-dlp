from telebot.types import KeyboardButton, ReplyKeyboardMarkup, User
from dublib.Methods import WriteJSON
from Source.Users import UserData

def BuildMenu(User: UserData) -> ReplyKeyboardMarkup:
	# Текст кнопки: компрессия.
	Compression = "🔴 Отключить сжатие" if User.compression else "🟢 Включить сжатие"
	# Меню.
	Menu = ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	KB_Compression = KeyboardButton(Compression)
	# Добавление кнопок в меню.
	Menu.add(KB_Compression, row_width = 1)
	
	return Menu

def UpdatePremium(Settings: dict, UserData: User):
	# Обновление статуса.
	Settings["premium"] = bool(UserData.is_premium)
	# Сохранение статуса.
	WriteJSON("Settings.json", Settings)