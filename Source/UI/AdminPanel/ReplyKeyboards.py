from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboards:
	"""Генератор Reply-интерфейса."""

	def __init__(self):
		"""Генератор Reply-интерфейса."""

		pass

	def admin(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: панель управления."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Mailing = types.KeyboardButton("👤 Рассылка")
		Statistics = types.KeyboardButton("📊 Статистика")
		Close = types.KeyboardButton("❌ Закрыть")
		Menu.add(Mailing, Statistics, Close, row_width = 2)

		return Menu

	def cancel(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: отмена."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Cancel = types.KeyboardButton("❌ Отмена")
		Menu.add(Cancel)

		return Menu
	
	def editing(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: редактирование сообщения."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Ok = types.KeyboardButton("✅ Завершить")
		Cancel = types.KeyboardButton("❌ Отмена")
		Menu.add(Ok, Cancel, row_width = 1)

		return Menu
	
	def mailing(self, user: UserData) -> types.ReplyKeyboardMarkup:
		"""
		Строит кнопочный интерфейс: рассылка.
			user – администратор.
		"""

		ButtonText = "Удалить" if user.get_property("button_link") else "Добавить"
		Status = "🔴 Остановить" if user.get_property("mailing") else "🟢 Запустить"
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Start = types.KeyboardButton(Status)
		Sampling = types.KeyboardButton("🎯 Выборка")
		View = types.KeyboardButton("🔎 Просмотр")
		Edit = types.KeyboardButton("✏️ Редактировать")
		Button = types.KeyboardButton(f"🕹️ {ButtonText} кнопку")
		Back = types.KeyboardButton("↩️ Назад")
		Menu.add(Start, Sampling, View, Edit, Button, Back, row_width = 1)

		return Menu