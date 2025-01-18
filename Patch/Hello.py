from Source.Core.GetText import _

from dublib.TelebotUtils import UserData
from telebot import TeleBot, types

class PatchReplyKeyboards:
	"""Генератор Reply-интерфейса."""

	def __init__(self):
		"""Генератор Reply-интерфейса."""

		pass

	def main(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: главное меню."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Info = types.KeyboardButton(_("ℹ️ Инфа"))
		Rename = types.KeyboardButton(_("♻️ Изменить имя"))
		Support = types.KeyboardButton(_("💬 Поддержка"))
		Share = types.KeyboardButton(_("📢 Поделиться с друзьями"))
		Menu.add(Info, Rename, Support, Share, row_width = 1)

		return Menu

def Hello(bot: TeleBot, user: UserData):
	Name = None
	try:
		Name = user.get_property("name")
	except: pass

	Devices = types.InlineKeyboardMarkup()
	iPhone = types.InlineKeyboardButton("iPhone 🍎", callback_data = "device_iphone")
	Android = types.InlineKeyboardButton("Android 🤖", callback_data = "device_android")
	Devices.add(Android, iPhone, row_width = 2)

	if not Name:
		bot.send_message(user.id, _("Привет! Рад что ты обратился именно ко мне! ✊️"))
		bot.send_message(user.id, _("Как зовут тебя, воин?"))
		user.set_expected_type("user_name")

	else:
		Message = bot.send_message(user.id, _("Приветствую,") + f" {Name}!")
		user.set_temp_property("remove_message", Message.id)
		bot.send_message(user.id, _("Скажи, пожалуйста, какое у тебя устройство?"), reply_markup = Devices)

def AnswerName(bot: TeleBot, user: UserData, message: types.Message) -> bool:
	IsAnswered = False

	if user.expected_type == "user_name":
		Name = None
		try:
			Name = user.get_property("name")
		except: pass

		IsAnswered = True
		user.set_property("name", message.text)
		user.set_expected_type(None)
		Message = bot.send_message(user.id, _("Приятно познакомиться,") + f" {message.text}!)")
		user.set_temp_property("remove_message", Message.id)

		Devices = types.InlineKeyboardMarkup()
		iPhone = types.InlineKeyboardButton("iPhone 🍎", callback_data = "device_iphone")
		Android = types.InlineKeyboardButton("Android 🤖", callback_data = "device_android")
		Devices.add(Android, iPhone, row_width = 2)
		if Name: bot.send_message(user.id, _("А устройство я надеюсь ты не сменил?"), reply_markup = Devices)
		else: bot.send_message(user.id, _("Скажи, пожалуйста, какое у тебя устройство?"), reply_markup = Devices)

	return IsAnswered