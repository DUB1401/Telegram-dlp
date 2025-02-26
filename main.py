from dublib.Methods.Filesystem import MakeRootDirectories, ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.CLI.Terminalyzer import Command, Terminalyzer
from dublib.TelebotUtils import UsersManager
from dublib.Engine.GetText import GetText

from telebot import types, TeleBot
from urllib.parse import urlparse
from time import sleep

import re

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 12)
MakeRootDirectories(["Data/Users", "Temp", "yt-dlp"])
Clear()

Settings = ReadJSON("Settings.json")
Bot = TeleBot(Settings["token"])
LANGUAGE = Settings["language"]

GetText.initialize("Telegram-dlp", LANGUAGE, "Locales")
_ = GetText.gettext

from Source.UI.Templates import Animation, StepsIndicator
from Source.UI.InlineKeyboards import InlineKeyboards
from Source.Core.TelethonUser import TelethonUser
from Source.UI.TeleBotAdminPanel import Panel
from Source.Core.Storage import Storage
from Source.Core.YtDlp import YtDlp

from Patch.Menu import ButtonsDecorators, CommandsDecorators, InlineDecorators
from Patch.Data import INTERVAL, GenerateStartAnimation
from Patch.Hello import AnswerName, Hello
from Patch.YouTube import Trends
from Patch import Menu

Menu.BOT_NAME = Bot.get_me().username
Menu.SUPPORT = Settings["support_contact"]
TrendsObject = Trends(LANGUAGE != "ru")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

CommandsList = list()

Com = Command("upload", _("Выгружает файл на сервер Telegram."))
Com.add_key("file", important = True, description = _("Название файла."))
Com.add_key("site", important = True, description = _("Домен сайта."))
Com.add_key("user", important = True, description = _("Идентификатор пользователя Telegram."))
Com.add_key("name", description = _("Название файла в Telegram."))
Com.add_key("quality", important = True, description = _("Качество видео."))
Com.add_flag("c", _("Включает режим сжатия файла Telegram."))
Com.add_flag("r", _("Помечает формат как перекодированный в стандартный."))
Com.add_flag("w", _("Помечает формат как имеющий водяной знак."))
CommandsList.append(Com)

Com = Command("login", _("Выполняет вход в аккаунт."))
Com.add_argument(important = True, description = _("Номер телефона."))
Com.add_argument(important = True, description = _("API ID пользователя."))
Com.add_argument(important = True, description = _("API Hash пользователя."))
CommandsList.append(Com)

Analyzer = Terminalyzer()
Analyzer.enable_help(True)
Analyzer.help_translation.command_description = _("Выводит список поддерживаемых команд. Добавьте название другой команды в качестве аргумента для подробностей.")
Analyzer.help_translation.important_note = ""
ParsedCommand = Analyzer.check_commands(CommandsList)

#==========================================================================================#
# >>>>> ОБРАБОТКА CLI <<<<< #
#==========================================================================================#

if ParsedCommand and ParsedCommand.name == "help":
	exit(0)

if ParsedCommand and ParsedCommand.name == "upload":
	Filename = ParsedCommand.get_key_value("file")
	UserID = ParsedCommand.get_key_value("user")
	Site = ParsedCommand.get_key_value("site")
	Name = ParsedCommand.get_key_value("name")
	Quality = ParsedCommand.get_key_value("quality")
	Compression = ParsedCommand.check_flag("c")
	Recoding = ParsedCommand.check_flag("r")
	Watermarked = ParsedCommand.check_flag("w")
	User = TelethonUser(Bot.get_me().username)
	User.initialize()
	Result = User.upload_file(UserID, Site, Filename, Quality, Compression, Recoding, Watermarked, Name)
	if Result: exit(0)
	else: exit(1)
	
elif ParsedCommand and ParsedCommand.name == "login":
	User = TelethonUser(Bot.get_me().username)
	User.login(ParsedCommand.arguments[0], ParsedCommand.arguments[1], ParsedCommand.arguments[2])
	
else:
	Users = UsersManager("Data/Users")
	StorageBox = Storage("Storage")
	Downloader = YtDlp(StorageBox, Settings)
	AdminPanel = Panel()

	#==========================================================================================#
	# >>>>> ОБРАБОТКА КОММАНД <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.commands(Bot, Users, Settings["password"])
	CommandsDecorators(Bot, Users)

	@Bot.message_handler(commands = ["about"])
	def CommandAbout(Message: types.Message):
		User = Users.auth(Message.from_user)
		Bot.send_message(
			chat_id = Message.chat.id,
			text = _("<b>Telegram-dlp</b> является Open Source проектом под лицензией Apache 2.0 за авторством <a href=\"https://github.com/DUB1401\">@DUB1401</a> и использует библиотеку <a href=\"https://github.com/yt-dlp/yt-dlp\">yt-dlp</a>. Исходный код и документация доступны в <a href=\"https://github.com/DUB1401/Telegram-dlp\">этом</a> репозитории."),
			parse_mode = "HTML",
			disable_web_page_preview = True
		)
	
	@Bot.message_handler(commands = ["settings"])
	def CommandStart(Message: types.Message):
		User = Users.auth(Message.from_user)

		Bot.send_message(
			chat_id = Message.chat.id,
			text = _("Настройте <b>Telegram-dlp</b> под себя!\n\n<b>Сжатие</b> – управляет сжатием видеофайлов на стороне Telegram. При отключённом состоянии все видео будут отправляться как документы.\n\n<b>Перекодирование</b> – преобразует все форматы мультимедиа в <i>MP4</i> и <i>M4A</i>. При отключённом состоянии будут отправляться нативные файлы (зачастую гораздо быстрее, особенно для <a href=\"https://www.youtube.com\">YouTube</a>.\n\n<b>Архив</b> – для некоторых источников бот сохраняет параметры для загрузки видео. Вы можете воспользоваться архивными данными для моментального перехода к выбору скачиваемого файла, но эти сведения время от времени устаревают.\n\n<b>Хранилище</b> – если файл уже загружался кем-либо до вас, вы можете получить его моментально из хранилища."),
			parse_mode = "HTML",
			disable_web_page_preview = True,
			reply_markup = InlineKeyboards().options(User)
		)

	@Bot.message_handler(commands = ["start"])
	def CommandStart(Message: types.Message):
		User = Users.auth(Message.from_user)
		User.set_property("option_compression", True, force = False)
		User.set_property("option_recoding", True, force = False)
		User.set_property("option_archive", True, force = False)
		User.set_property("option_storage", True, force = False)
		User.set_property("is_downloading", False)
		Hello(Bot, User)
		
	@Bot.message_handler(commands = ["support"])
	def CommandAbout(Message: types.Message):
		User = Users.auth(Message.from_user)
		if Settings["support_contact"]: Bot.send_message(
			chat_id = Message.chat.id,
			text = _("Возникли проблемы? Сообщите о них сюда:") + " " + Settings["support_contact"],
			parse_mode = "HTML",
			disable_web_page_preview = True
		)

	@Bot.message_handler(func = lambda Message: re.match(r"^/dm([1-9]|1[0-9]|20)$", Message.text))
	def CommandDownloadMusic(Message: types.Message):
		Index = int(Message.text[3:]) - 1
		Message.text = TrendsObject.get_music()[Index].link
		Text(Message)

	@Bot.message_handler(func = lambda Message: re.match(r"^/dn([1-9]|1[0-9]|20)$", Message.text))
	def CommandDownloadMusic(Message: types.Message):
		Index = int(Message.text[3:]) - 1
		Message.text = TrendsObject.get_news()[Index].link
		Text(Message)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА REPLY-КНОПОК <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.reply_keyboards(Bot, Users)
	ButtonsDecorators(Bot, Users)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА ВВОДА ТЕКСТА <<<<< #
	#==========================================================================================#

	@Bot.message_handler(content_types = ["text"])
	def Text(Message: types.Message):
		User = Users.auth(Message.from_user)
		if AnswerName(Bot, User, Message): return
		if AdminPanel.procedures.text(Bot, User, Message): return

		if User.get_property("is_downloading"):
			Bot.send_message(chat_id = Message.chat.id, text = _("Кажется, вы уже скачиваете файл. Если это не так, перезапустите бот командой /start для проверки."))
			return

		if urlparse(Message.text).scheme:
			SendedMessage = Bot.send_message(
				chat_id = Message.chat.id,
				text = _("Идёт получение данных...")
			)
			
			Site = StorageBox.parse_site_name(Message.text)
			Link = None
			VideoID = None
			Info = None

			if Site:
				Link = StorageBox.check_link(Site, Message.text)

				if StorageBox.check_for_playlist(Site, Link):
					Bot.edit_message_text(
						message_id = SendedMessage.id,
						chat_id = Message.chat.id,
						text = _("Похоже это ссылка на плейлист или джем. А мне нужна именно на ролик 🙄")
					)
					return

				VideoID = StorageBox.parse_video_id(Site, Link)
				Info = StorageBox.get_info(Site, VideoID)
				if not Info or not User.get_property("option_archive"): Info = Downloader.get_info(Link)

			if Info:

				if "duration" in Info.keys() and type(Info["duration"]) == int and Info["duration"] >= 14400: 
					Bot.edit_message_text(
						message_id = SendedMessage.id,
						chat_id = Message.chat.id,
						text = ("Видео слишком большое. Такое не поместится в Telegram 😬")
					)
					return

				# Для TikTok обязательно пометить хотя бы однин ролик как HD.
				if Info["webpage_url_domain"] == "tiktok.com":
					IsHD = False
					Mini = dict()
					for Format in Info["formats"]: 
						if "width" in Format.keys() and Format["width"] == 576: Mini = Format

						if "width" in Format.keys() and Format["width"] == 720: 
							IsHD = True
							break

					if not IsHD and Mini:
						Mini["resolution"] = "720x1280"
						Info["formats"].append(Mini)

				StorageBox.save_info(Site, VideoID, Info)
				User.set_temp_property("link", Link)
				User.set_temp_property("site", Site)
				User.set_temp_property("video_id", Info["id"])
				User.set_temp_property("filename", Info["title"])
				Bot.delete_message(message_id = SendedMessage.id, chat_id = Message.chat.id)
				InlineKeyboards().send_format_selector(Bot, Message.chat.id, Info, StorageBox, Settings)

			else:
				Bot.edit_message_text(
					message_id = SendedMessage.id,
					chat_id = Message.chat.id,
					text = _("Эта ссылка не может быть обработана, поскольку не содержит видео. Все проверьте и отправьте мне правильную! 🤌")
				)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = _("Эта ссылка не может быть обработана. Все проверьте и отправьте мне правильную! 🤌")
			)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА INLINE-КНОПОК <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.inline_keyboards(Bot, Users)
	InlineDecorators(Bot, Users, TrendsObject)

	@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("option_"))
	def InlineButton(Call: types.CallbackQuery):
		User = Users.auth(Call.from_user)
		CallbackData = Call.data.split("_")
		Option = CallbackData[1]
		Value = True if CallbackData[2] == "enable" else False
		User.set_property("option_" + Option, Value)
		Bot.edit_message_reply_markup(Call.message.chat.id, Call.message.id, reply_markup = InlineKeyboards().options(User))
		Bot.answer_callback_query(Call.id)

	@Bot.callback_query_handler(func = lambda Callback: Callback.data == "download_audio")
	def InlineButton(Call: types.CallbackQuery):
		User = Users.auth(Call.from_user)
		Bot.answer_callback_query(Call.id)
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		User.set_property("is_downloading", True)
		Link = User.get_property("link")
		VideoID = User.get_property("video_id")
		Quality = "audio"
		Site = User.get_property("site")
		Name = User.get_property("filename")
		Compression = User.get_property("option_compression")
		Recoding = User.get_property("option_recoding")
		FileMessageID = StorageBox.get_file_message_id(Site, VideoID, Quality, Compression, Recoding)

		Procedures = [
			_("Скачиваю аудио..."),
			_("Выгружаю аудио в Telegram..."),
			_("Отправляю...")
		]
		Episodes = ReadJSON(f"Patch/Cartoons/{LANGUAGE}.json")
		ProgressAnimation = list()

		for Key in Episodes["episodes"].keys():
			Buffer = Animation()
			Buffer.set_interval(INTERVAL)
			for Line in Episodes["episodes"][Key]: Buffer.add_lines(Line)
			ProgressAnimation.append(Buffer)

		SI = StepsIndicator(Bot, Call.message.chat.id, Procedures, parse_mode = "HTML")

		if FileMessageID[0] and User.get_property("option_storage"):
			Bot.copy_message(Call.message.chat.id, FileMessageID[0], FileMessageID[1], caption = "@" + Bot.get_me().username)

		else:
			SI.set_title(_("%s\n\n<b>Результат процесса:</b>\n"))
			SI.send()
			SI.start_animation(ProgressAnimation, GenerateStartAnimation(Episodes["name"]))
			Result = Downloader.download_audio(Link, f"Temp/{User.id}/", VideoID, recoding = Recoding)
			
			if Result:
				SI.next(_("Аудио скачано!"))
				Result = StorageBox.upload_file(User.id, Site, Result, Quality, Compression, Recoding, name = Name)

				if Result:
					SI.next(_("Аудио загружено в Telegram!"))
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression, Recoding)

					if Result.code == 0:
						Bot.copy_message(Call.message.chat.id, Result["chat_id"], Result["message_id"], caption = "@" + Bot.get_me().username)
						SI.stop_animation()
						SI.set_footer(_("\n<b><i>Наслаждайтесь вашим аудио,") + " " + User.get_property("name") + "!</i></b> 😘")
						SI.next(_("Отправлено!"))

					else: SI.error(_("Не удалось отправить аудио!"))

				else: SI.error(_("Не удалось загрузить аудио в Telegram!"))

			else: SI.error(_("Не удалось скачать аудио!"))

		User.set_property("is_downloading", False)
		User.clear_temp_properties()

	@Bot.callback_query_handler(func = lambda Callback: Callback.data.count("video") or Callback.data.count("watermarked"))
	def InlineButton(Call: types.CallbackQuery):
		User = Users.auth(Call.from_user)
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		
		IsWatermarked = True if "watermarked" in Call.data else False
		Query = Call.data.replace("download_watermarked_" if IsWatermarked else "download_video_", "").replace("%", " ")
		Link = User.get_property("link")
		VideoID = User.get_property("video_id")
		Quality = Query.split("+")[0]
		FormatID = Query.split("+")[1]
		Site = User.get_property("site")
		Name = User.get_property("filename")
		Compression = User.get_property("option_compression")
		Recoding = User.get_property("option_recoding")

		Procedures = [
			_("Скачиваю видео..."),
			_("Улучшаю качество..."),
			_("Выгружаю видео в Telegram..."),
			_("Отправляю...")
		]
		Episodes = ReadJSON(f"Patch/Cartoons/{LANGUAGE}.json")
		ProgressAnimation = list()

		for Key in Episodes["episodes"].keys():
			Buffer = Animation()
			Buffer.set_interval(INTERVAL)
			for Line in Episodes["episodes"][Key]: Buffer.add_lines(Line)
			ProgressAnimation.append(Buffer)

		if not Settings["quality_improvement"]: Procedures.pop(1)
		SI = StepsIndicator(Bot, Call.message.chat.id, Procedures, parse_mode = "HTML")

		if Quality == "null": Quality = None
		FileMessageID = StorageBox.get_file_message_id(Site, VideoID, Quality, Compression, Recoding, watermarked = IsWatermarked)

		if FileMessageID[0] and User.get_property("option_storage"):
			Bot.copy_message(Call.message.chat.id, FileMessageID[0], FileMessageID[1], caption = "@" + Bot.get_me().username)

		else:
			User.set_property("is_downloading", True)
			SI.set_title(_("%s\n\n<b>Результат процесса:</b>\n"))
			SI.send()
			SI.start_animation(ProgressAnimation, GenerateStartAnimation(Episodes["name"]))
			Result = Downloader.download_video(Link, f"Temp/{User.id}/", VideoID, FormatID, recoding = Recoding)
			
			if Result:

				if Settings["quality_improvement"]:
					SI.next(_("Видео скачано!"))
					sleep(4)
					SI.next(_("Качество улучшено!"))

				else: SI.next(_("Видео скачано!"))

				Result = StorageBox.upload_file(User.id, Site, Result, Quality, Compression, Recoding, watermarked = IsWatermarked, name = Name)

				if Result:
					SI.next(_("Видео загружено в Telegram!"))
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression, Recoding, watermarked = IsWatermarked)

					if Result.code == 0:
						Bot.copy_message(Call.message.chat.id, Result["chat_id"], Result["message_id"], caption = "@" + Bot.get_me().username)
						SI.stop_animation()
						SI.set_footer(_("\n<b><i>Наслаждайтесь вашим видео,") + " " + User.get_property("name") + "!</i></b> 😘")
						SI.next(_("Отправлено!"))

					else: SI.error(_("Не удалось отправить видео!"))

				else: SI.error(_("Не удалось загрузить видео в Telegram!"))

			else: SI.error(_("Не удалось скачать видео!"))

		User.set_property("is_downloading", False)
		User.clear_temp_properties()

	#==========================================================================================#
	# >>>>> ОБРАБОТКА ФАЙЛОВ <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.photo(Bot, Users)

	@Bot.message_handler(content_types = ["audio", "document", "video", "voice"])
	def File(Message: types.Message):
		User = Users.auth(Message.from_user)
		AdminPanel.procedures.files(Bot, User, Message)

		if Message.from_user.id in Settings["trusted_sources_id"]: 
			FileData = Message.caption.split("\n")
			Site = FileData[0]
			VideoID = FileData[1]
			Quality = FileData[2]
			Compression = True if FileData[3].endswith("on") else False
			Recoding = True if FileData[4].endswith("on") else False
			Watermarked = True if FileData[5].endswith("on") else False
			if Quality == "None": Quality = None
			StorageBox.register_file(Site, VideoID, Quality, Compression, Recoding, Watermarked, Message.id, User.id)

	Bot.infinity_polling()