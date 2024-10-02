from Source.UI.Templates import Animation, StepsIndicator
from Source.UI.InlineKeyboards import InlineKeyboards
from Source.Core.TelethonUser import TelethonUser
from Source.Core.Storage import Storage
from Source.UI.AdminPanel import Panel
from Source.Core.YtDlp import YtDlp

from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.CLI.Terminalyzer import Command, Terminalyzer
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils import UsersManager
from dublib.Methods.JSON import ReadJSON
from telebot import types, TeleBot
from urllib.parse import urlparse
from time import sleep

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 12)
MakeRootDirectories(["Data/Users", "Temp"])
Clear()

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

Settings = ReadJSON("Settings.json")
if type(Settings["token"]) != str or Settings["token"].strip() == "": raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

CommandsList = list()

Com = Command("upload", "Выгружает файл на сервер Telegram.")
Com.add_key("file", important = True, description = "Название файла.")
Com.add_key("site", important = True, description = "Домен сайта.")
Com.add_key("user", important = True, description = "Идентификатор пользователя Telegram.")
Com.add_key("name", description = "Название файла в Telegram.")
Com.add_key("quality", important = True, description = "Качество видео.")
Com.add_flag("c", "Включает режим сжатия файла Telegram.")
Com.add_flag("r", "Помечает формат как перекодированный в стандартный.")
Com.add_flag("w", "Помечает формат как имеющий водяной знак.")
CommandsList.append(Com)

Com = Command("login", "Выполняет вход в аккаунт.")
Com.add_argument(important = True, description = "Номер телефона.")
Com.add_argument(important = True, description = "API ID пользователя.")
Com.add_argument(important = True, description = "API Hash пользователя.")
CommandsList.append(Com)

Analyzer = Terminalyzer()
Analyzer.enable_help(True)
Analyzer.help_translation.help_command_description = "Выводит список поддерживаемых команд. Добавьте название другой команды в качестве аргумента для подробностей."
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
	User = TelethonUser(Settings["bot_name"])
	User.initialize()
	Result = User.upload_file(UserID, Site, Filename, Quality, Compression, Recoding, Watermarked, Name)
	if Result: exit(0)
	else: exit(1)
	
elif ParsedCommand and ParsedCommand.name == "login":
	User = TelethonUser(Settings["bot_name"])
	User.login(ParsedCommand.arguments[0], ParsedCommand.arguments[1], ParsedCommand.arguments[2])
	
else:
	Bot = TeleBot(Settings["token"])
	Users = UsersManager("Data/Users")
	StorageBox = Storage("Storage", Settings["venv"])
	Downloader = YtDlp(StorageBox, "yt-dlp/yt-dlp", Settings["proxy"], modules = Settings["modules"])
	AdminPanel = Panel()

	#==========================================================================================#
	# >>>>> ОБРАБОТКА КОММАНД <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.commands(Bot, Users, Settings["password"])

	@Bot.message_handler(commands = ["about"])
	def CommandAbout(Message: types.Message):
		User = Users.auth(Message.from_user)
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*Telegram\\-dlp* является Open Source проектом под лицензией Apache 2\\.0 за авторством [@DUB1401](https://github.com/DUB1401)\\ и использует библиотеку [yt\\-dlp](https://github.com/yt-dlp/yt-dlp)\\. Исходный код и документация доступны в [этом](https://github.com/DUB1401/Telegram-dlp) репозитории\\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)
	
	@Bot.message_handler(commands = ["settings"])
	def CommandStart(Message: types.Message):
		User = Users.auth(Message.from_user)

		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Настройте *Telegram\\-dlp* под себя\\!\n\n*Сжатие* – управляет сжатием видеофайлов на стороне Telegram\\. При отключённом состоянии все видео будут отправляться как документы\\.\n\n*Перекодирование* – преобразует все форматы мультимедиа в _MP4_ и _M4A_\\. При отключённом состоянии будут отправляться нативные файлы \\(зачастую гораздо быстрее, особенно для [YouTube](https://www.youtube.com/)\\)\\.\n\n*Архив* – для некоторых источников бот сохраняет данные для загрузки видео\\. Вы можете воспользоваться архивными данными для моментального перехода к выбору скачиваемого файла, но эти сведения время от времени устаревают\\.\n\n*Хранилище* – если файл уже загружался кем\\-либо до вас, вы можете получить его моментально из хранилища\\.",
			parse_mode = "MarkdownV2",
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
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*Telegram\\-dlp* поможет вам скачать видео или извлечь из них аудиодорожки\\. Поддерживается широкий список [источников](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)\\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)
		
	#==========================================================================================#
	# >>>>> ОБРАБОТКА REPLY-КНОПОК <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.reply_keyboards(Bot, Users)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА ВВОДА ТЕКСТА <<<<< #
	#==========================================================================================#

	@Bot.message_handler(content_types = ["text"])
	def Text(Message: types.Message):
		User = Users.auth(Message.from_user)
		if AdminPanel.procedures.text(Bot, User, Message): return

		if User.get_property("is_downloading"):
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы уже скачиваете видеоролик."
			)

		elif urlparse(Message.text).scheme:
			SendedMessage = Bot.send_message(
				chat_id = Message.chat.id,
				text = "Идёт получение данных..."
			)
			Site = StorageBox.parse_site_name(Message.text)
			Link = StorageBox.check_link(Message.text)
			VideoID = None
			Info = None

			if Site:
				VideoID = StorageBox.parse_video_id(Site, Link)
				Info = StorageBox.get_info(Site, VideoID)
				if not Info: Info = Downloader.get_info(Link)

			if Info:
				StorageBox.save_info(Site, VideoID, Info)
				User.set_temp_property("link", Link)
				User.set_temp_property("site", Site)
				User.set_temp_property("video_id", Info["id"])
				User.set_temp_property("filename", Info["title"])
				Bot.delete_message(message_id = SendedMessage.id, chat_id = Message.chat.id)
				InlineKeyboards().send_fromat_selector(Bot, Message.chat.id, Info, Settings["one_watermarked"])

			else:
				Bot.edit_message_text(
					message_id = SendedMessage.id,
					chat_id = Message.chat.id,
					text = "Мне не удалось обнаружить видео по этой ссылке."
				)

		else:
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Ваше сообщение не является ссылкой. Попробуйте ещё раз."
			)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА INLINE-КНОПОК <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.inline_keyboards(Bot, Users)

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
		
		ProgressAnimation = Animation()
		ProgressAnimation.set_interval(1)
		ProgressAnimation.add_lines("\\.")
		ProgressAnimation.add_lines("\\.\\.")
		ProgressAnimation.add_lines("\\.\\.\\.")
		ProgressAnimation.add_lines("")

		Procedures = [
			"Скачиваю аудио%s",
			"Выгружаю аудио в Telegram%s",
			"Отправляю%s"
		]

		SI = StepsIndicator(Bot, Call.message.chat.id, Procedures, parse_mode = "MarkdownV2")

		if FileMessageID[0] and User.get_property("option_storage"):
			Bot.copy_message(Call.message.chat.id, FileMessageID[0], FileMessageID[1], caption = "@" + Settings["bot_name"])

		else:
			SI.send()
			SI.start_animation(ProgressAnimation)
			Result = Downloader.download_audio(Link, f"Temp/{User.id}/", VideoID, recoding = Recoding)
			
			if Result:
				SI.next("Аудио скачано\\.")
				Result = StorageBox.upload_file(User.id, Site, Result, Quality, Compression, Recoding, name = Name)

				if Result:
					SI.next("Аудио загружено в Telegram\\.")
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression, Recoding)

					if Result.code == 0:
						Bot.copy_message(Call.message.chat.id, Result["chat_id"], Result["message_id"], caption = "@" + Settings["bot_name"])
						SI.next("Отправлено\\.")

					else: SI.error("Не удалось отправить видео\\.")

				else: SI.error("Не удалось загрузить аудио в Telegram\\.")

			else: SI.error("Не удалось скачать аудио\\.")

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

		ProgressAnimation = Animation()
		ProgressAnimation.set_interval(1)
		ProgressAnimation.add_lines("\\.")
		ProgressAnimation.add_lines("\\.\\.")
		ProgressAnimation.add_lines("\\.\\.\\.")
		ProgressAnimation.add_lines("")

		Procedures = [
			"Скачиваю видео%s",
			"Улучшаю качество%s",
			"Выгружаю видео в Telegram%s",
			"Отправляю%s"
		]

		if not Settings["quality_improvement"]: Procedures.pop(1)
		SI = StepsIndicator(Bot, Call.message.chat.id, Procedures, parse_mode = "MarkdownV2")

		if Quality == "null": Quality = None
		FileMessageID = StorageBox.get_file_message_id(Site, VideoID, Quality, Compression, Recoding, watermarked = IsWatermarked)

		if FileMessageID[0] and User.get_property("option_storage"):
			Bot.copy_message(Call.message.chat.id, FileMessageID[0], FileMessageID[1], caption = "@" + Settings["bot_name"])

		else:
			User.set_property("is_downloading", True)
			SI.send()
			SI.start_animation(ProgressAnimation)
			Result = Downloader.download_video(Link, f"Temp/{User.id}/", VideoID, FormatID, recoding = Recoding)

			if Result:

				if Settings["quality_improvement"]:
					SI.next("Видео скачано\\.")
					sleep(4)
					SI.next("Качество улучшено\\.")

				else: SI.next("Видео скачано\\.")

				Result = StorageBox.upload_file(User.id, Site, Result, Quality, Compression, Recoding, watermarked = IsWatermarked, name = Name)

				if Result:
					SI.next("Видео загружено в Telegram\\.")
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression, Recoding, watermarked = IsWatermarked)

					if Result.code == 0:
						Bot.copy_message(Call.message.chat.id, Result["chat_id"], Result["message_id"], caption = "@" + Settings["bot_name"])
						SI.next("Отправлено\\.")

					else: SI.error("Не удалось отправить видео\\.")

				else: SI.error("Не удалось загрузить видео в Telegram\\.")

			else: SI.error("Не удалось скачать видео\\.")

		User.set_property("is_downloading", False)
		User.clear_temp_properties()

	#==========================================================================================#
	# >>>>> ОБРАБОТКА ФАЙЛОВ <<<<< #
	#==========================================================================================#

	AdminPanel.decorators.photo(Bot, Users)

	@Bot.message_handler(content_types = ["audio", "document", "video"])
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