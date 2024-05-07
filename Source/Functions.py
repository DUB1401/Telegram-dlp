from telebot.types import KeyboardButton, ReplyKeyboardMarkup, User
from Source.MessageBox import MessageBox
from dublib.TelebotUtils import UserData
from dublib.Methods import WriteJSON

import telebot

def BuildMenu(User: UserData, Text: MessageBox) -> ReplyKeyboardMarkup:
	# Модификация ключа текста кнопки.
	CompressionStatus = "off" if User.get_property("compression") else "on"
	# Текст кнопки: компрессия.
	Compression = Text.get(f"button-compression-{CompressionStatus}", language = User.language)
	# Меню.
	Menu = ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	KB_Compression = KeyboardButton(Compression)
	# Добавление кнопок в меню.
	Menu.add(KB_Compression, row_width = 1)
	
	return Menu

def BuildResolutions(Resolutions: list[str]) -> ReplyKeyboardMarkup:
	# Список разрешений.
	ResolutionsMenu = ReplyKeyboardMarkup(resize_keyboard = True)
	# Для каждого разрешения создать кнопку.
	for Resolution in Resolutions: ResolutionsMenu.add("🎬 " + Resolution)
	
	return ResolutionsMenu

def UpdatePremium(Settings: dict, UserData: User):
	# Обновление статуса.
	Settings["premium"] = bool(UserData.is_premium)
	# Сохранение статуса.
	WriteJSON("Settings.json", Settings)