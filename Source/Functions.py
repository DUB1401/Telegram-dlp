from telebot.types import KeyboardButton, ReplyKeyboardMarkup, User
from Source.MessageBox import MessageBox
from dublib.Methods import WriteJSON
from Source.Users import UserData

def BuildMenu(User: UserData, Text: MessageBox) -> ReplyKeyboardMarkup:
	# Модификация ключа текста кнопки.
	CompressionStatus = "on" if User.compression else "off"
	# Текст кнопки: компрессия.
	Compression = Text.get(f"button-compression-{CompressionStatus}", language = User.language)
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