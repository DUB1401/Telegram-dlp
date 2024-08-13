from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:
	"""Генератор Inline-интерфейса."""

	def __init__(self):
		"""Генератор Inline-интерфейса."""

		pass
	
	def sampling(admin: UserData):
		"""
		Строит Inline-интерфейс: выборка.
			admin – администратор.
		"""

		#---> Генерация кнопочного интерфейса.
		#==========================================================================================#
		Menu = types.InlineKeyboardMarkup()
		LastSampling = types.InlineKeyboardButton("1K", callback_data = "sampling_last")
		AllSampling = types.InlineKeyboardButton("Все", callback_data = "sampling_all")
		Cancel = types.InlineKeyboardButton("Отмена", callback_data = "sampling_cancel")
		Menu.add(LastSampling, AllSampling, row_width = 2)
		Menu.add(Cancel, row_width = 1)

		return Menu
		