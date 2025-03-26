from Patch.Hello import PatchReplyKeyboards
from Patch.YouTube import Trends

from dublib.TelebotUtils import TeleCache, UsersManager
from dublib.Methods.Filesystem import ReadJSON
from dublib.Engine.GetText import _
from dublib.Polyglot import HTML

from datetime import datetime
from telebot import TeleBot, types
from time import sleep

BOT_NAME = ""
SETTINGS = None

Cacher = TeleCache()

class PatchInlineKeyboards:
	"""Генератор кнопочного интерфейса."""

	def __init__(self):
		"""Генератор кнопочного интерфейса."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Settings = ReadJSON("Patch/Settings.json")

	def ok(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()
		Button = types.InlineKeyboardButton(_("Всё ясно!"), callback_data = "delete_message")
		Menu.add(Button, row_width = 1)

		return Menu
	
	def share(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = "\n\n" +  HTML(self.__Settings["bot_title"]).plain_text + "\n" + _("Лучший бот для скачивания видео 🎬 и аудио 🎵 со всех популярных медиа площадок!")
			)
		
		Menu.add(Share)

		return Menu
	
	def support(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()
		Support = types.InlineKeyboardButton(_("Спасибо, все хорошо!"), callback_data = "delete_message")
		
		Menu.add(Support)

		return Menu
	
	def trends(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()
		News = types.InlineKeyboardButton(_("TOP 20 Videos YouTube") + " 📹", callback_data = "trends_news")
		Music = types.InlineKeyboardButton(_("TOP 20 Music YouTube") + " 🎵", callback_data = "trends_music")
		Menu.add(News, Music, row_width = 1)

		return Menu

def ButtonsDecorators(bot: TeleBot, users: UsersManager):
	Settings = ReadJSON("Patch/Settings.json")

	@bot.message_handler(content_types = ["text"], regexp = _("📢 Поделиться с друзьями"))
	def Button(Message: types.Message):
		User = users.auth(Message.from_user)
		File = Settings["share_image"]

		if not Settings["share_image"].startswith("http"):
			Cacher.set_options(SETTINGS["token"], SETTINGS["trusted_sources_id"][0])
			CachedFile = Cacher.get_real_cached_file(Settings["share_image"], autoupload_type = types.InputMediaPhoto)
			File = CachedFile.file_id

		bot.send_photo(
			Message.chat.id,
			photo = File,
			caption = "@%s\n@%s\n@%s\n\n" % (BOT_NAME, BOT_NAME, BOT_NAME) + Settings["bot_title"] + "\n" + _("Лучший бот для скачивания видео 🎬 и аудио 🎵 со всех популярных медиа площадок!") + "\n\n<b><i>" + _("Пользуйся и делись с друзьями!") + "</i></b>",
			reply_markup = PatchInlineKeyboards().share(),
			parse_mode = "HTML"
		)
		
	@bot.message_handler(content_types = ["text"], regexp = _("♻️ Изменить имя"))
	def Text(Message: types.Message):
		User = users.auth(Message.from_user)
		bot.send_message(User.id, _("Ну и какое на этот раз?) Удиви! 😄"))
		User.set_expected_type("user_name")

	@bot.message_handler(content_types = ["text"], regexp = _("💬 Поддержка"))
	def Text(Message: types.Message):
		User = users.auth(Message.from_user)
		bot.send_message(
			chat_id = Message.chat.id,
			text = _("Друзья, если у вас вдруг возникают какие-то проблемы при скачивании, то не стесняйтесь, делайте скриншот и пишите вот сюда 👇👇👇\n\n@%s\n\nСделаем наш сервис для вас еще лучше! 😉") % SETTINGS["support_contact"],
			reply_markup = PatchInlineKeyboards().support()
		)

	@bot.message_handler(content_types = ["text"], regexp = _("🔥 YouTube Trends"))
	def Button(Message: types.Message):
		User = users.auth(Message.from_user)

		bot.send_message(
			Message.chat.id,
			text = _("🔥 YouTube Trends") + " " + datetime.now().date().strftime("%d.%m.%Y"),
			reply_markup = PatchInlineKeyboards().trends()
		)

def CommandsDecorators(bot: TeleBot, users: UsersManager):

	@bot.message_handler(commands = ["info"])
	def CommandInfo(Message: types.Message):
		User = users.auth(Message.from_user)
		bot.send_message(
			Message.chat.id,
			text = _("@%s предназначен для скачивания видео 📺 и аудио 📻 с самых популярных медиа площадок, таких как: VK, YouTube, TikTok, Instagram и др.\n\nДля использования просто отправьте боту нужную ссылку и дождитесь, пока он предоставит вам уже готовый ролик! 🦾\n\nВы можете выбрать любое качество, которое вам подходит больше всего, а также можете скачать <b>только аудио</b> из абсолютно любого видеоролика!\n\n<b><i>Наслаждайтесь, и делитесь с друзьями!</i></b>") % BOT_NAME,
			parse_mode = "HTML",
			reply_markup = PatchInlineKeyboards().ok()
		)

def InlineDecorators(bot: TeleBot, users: UsersManager, trender: Trends):

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "delete_message")
	def InlineButton(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)
		bot.delete_message(User.id, Call.message.id)

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("device_"))
	def InlineButton(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)
		Device = Call.data.split("_")[-1]
		User.set_property("option_recoding", False if Device == "android" else True)

		try:
			MessageID = User.get_property("remove_message")
			bot.delete_messages(User.id, [MessageID, Call.message.id])

		except: bot.delete_message(User.id, Call.message.id)

		bot.send_message(User.id, _("Спасибо! Это для лучшей адаптации видео под тебя!"))
		sleep(0.5)
		bot.send_message(User.id, _("Кидай мне ссылку, и я тебе скачаю любой видос! 👌"), reply_markup = PatchReplyKeyboards().main())

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "trends_news")
	def InlineButton(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)
		News = trender.get_news()
		Text = "<b>" + _("TOP 20 Videos YouTube") + "</b> 📹\n\n" + _("● Нажми на позицию\n● Скопируй ссылку\n● Отправь её боту 😉") + "\n\n"
		Count = 20 if len(News) > 20 else len(News)
		for Index in range(20): Text += str(Index + 1) + ". <a href=\"" + News[Index].link + "\">" + News[Index].title + "</a>\n"
		
		bot.send_message(
			Call.message.chat.id,
			text = Text,
			parse_mode = "HTML",
			disable_web_page_preview = True
		)
		bot.answer_callback_query(Call.id)

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "trends_music")
	def InlineButton(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)
		Music = trender.get_music()
		Text = "<b>" + _("TOP 20 Music YouTube") + "</b> 🎵\n\n" + _("● Нажми на позицию\n● Скопируй ссылку\n● Отправь её боту 😉") + "\n\n"
		Count = 20 if len(Music) > 20 else len(Music)
		for Index in range(Count): Text += str(Index + 1) + ". <a href=\"" + Music[Index].link + "\">" + Music[Index].title + "</a>\n"

		bot.send_message(
			Call.message.chat.id,
			text = Text,
			parse_mode = "HTML",
			disable_web_page_preview = True
		)
		bot.answer_callback_query(Call.id)