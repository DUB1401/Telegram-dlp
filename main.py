from Source.Functions import SendFormatSelector
from Source.TelethonUser import TelethonUser
from Source.Storage import Storage
from Source.YtDlp import YtDlp

from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.CLI.Terminalyzer import Command, Terminalyzer
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils import UsersManager
from dublib.Methods.JSON import ReadJSON
from telebot import types, TeleBot
from urllib.parse import urlparse

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Data/Storage", "Data/Users", "Temp"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")
# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "": raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: upload.
Com = Command("upload", "Выгружает файл на сервер Telegram.")
Com.add_key("file", important = True, description = "Название файла.")
Com.add_key("site", important = True, description = "Домен сайта.")
Com.add_key("user", important = True, description = "Идентификатор пользователя Telegram.")
Com.add_key("quality", important = True, description = "Качество видео.")
Com.add_flag("c", "Включает режим сжатия файла Telegram.")
CommandsList.append(Com)

# Создание команды: login.
Com = Command("login", "Выполняет вход в аккаунт.")
Com.add_argument(important = True, description = "Номер телефона.")
Com.add_argument(important = True, description = "API ID пользователя.")
Com.add_argument(important = True, description = "API Hash пользователя.")
CommandsList.append(Com)

# Инициализация обработчика консольных аргументов.
Analyzer = Terminalyzer()
Analyzer.enable_help(True)
Analyzer.help_translation.help_command_description = "Выводит список поддерживаемых команд. Добавьте название другой команды в качестве аргумента для подробностей."
Analyzer.help_translation.important_note = ""
# Получение информации о проверке команд. 
ParsedCommand = Analyzer.check_commands(CommandsList)

#==========================================================================================#
# >>>>> ОБРАБОТКА CLI <<<<< #
#==========================================================================================#

# Обработка команды: help.
if ParsedCommand and ParsedCommand.name == "help":
	# Завершение работы.
	exit(0)

# Обработка команды: upload.
if ParsedCommand and ParsedCommand.name == "upload":
	# Получение данных.
	Filename = ParsedCommand.get_key_value("file")
	UserID = ParsedCommand.get_key_value("user")
	Site = ParsedCommand.get_key_value("site")
	Quality = ParsedCommand.get_key_value("quality")
	Compression = ParsedCommand.check_flag("c")
	# Инициализация пользователя.
	User = TelethonUser(Settings)
	User.initialize()
	# Выгрузка файла.
	Result = User.upload_file(UserID, Site, Filename, Quality, Compression)
	# Завершение работы.
	if Result: exit(0)
	else: exit(1)
	
# Обработка команды: login.
elif ParsedCommand and ParsedCommand.name == "login":
	# Инициализация пользователя.
	User = TelethonUser()
	# Авторизация.
	User.login(ParsedCommand.arguments[0], ParsedCommand.arguments[1], ParsedCommand.arguments[2])
	
# Запуск Telegram бота.
else:
	# Инициализация бота.
	Bot = TeleBot(Settings["token"])
	# Инициализация интерфейсов.
	Users = UsersManager("Data/Users")
	Downloader = YtDlp("yt-dlp/yt-dlp")
	StorageBox = Storage("Storage", Settings["venv"])

	#==========================================================================================#
	# >>>>> ОБРАБОТКА КОММАНД <<<<< #
	#==========================================================================================#
	
	# Обработка команды: about.
	@Bot.message_handler(commands = ["about"])
	def CommandAbout(Message: types.Message):
		# Авторизация пользователя.
		User = Users.auth(Message.from_user)
		# Отправка сообщения: информация о проекте.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*Telegram\\-dlp* является Open Source проектом под лицензией Apache 2\\.0 за авторством [@DUB1401](https://github.com/DUB1401)\\ и использует библиотеку [yt\\-dlp](https://github.com/yt-dlp/yt-dlp)\\. Исходный код и документация доступны в [этом](https://github.com/DUB1401/Telegram-dlp) репозитории\\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)
	
	# Обработка команды: disable_compression.
	@Bot.message_handler(commands = ["disable_compression"])
	def CommandEnableCompression(Message: types.Message):
		# Авторизация пользователя.
		User = Users.auth(Message.from_user)
		# Отключение сжатия.
		User.set_property("compression", False)
		# Отправка сообщения: сжатие включено.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Сжатие данных на стороне Telegram отключено."
		)

	# Обработка команды: enable_compression.
	@Bot.message_handler(commands = ["enable_compression"])
	def CommandEnableCompression(Message: types.Message):
		# Авторизация пользователя.
		User = Users.auth(Message.from_user)
		# Включение сжатия.
		User.set_property("compression", True)
		# Отправка сообщения: сжатие включено.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Сжатие данных на стороне Telegram включено."
		)

	# Обработка команды: start.
	@Bot.message_handler(commands = ["start"])
	def CommandStart(Message: types.Message):
		# Авторизация пользователя.
		User = Users.auth(Message.from_user)
		# Генерация свойств.
		User.set_property("compression", True, force = False)
		User.set_property("is_downloading", False)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "👋 Привет!\n\nЯ бот, помогающий скачивать видео и извлекать из них аудио. У меня очень широкий список поддерживаемых источников. Отправьте мне ссылку для начала работы."
		)
		
	#==========================================================================================#
	# >>>>> ОБРАБОТКА ВВОДА ТЕКСТА <<<<< #
	#==========================================================================================#

	# Обработка текстовых сообщений.
	@Bot.message_handler(content_types = ["text"])
	def Text(Message: types.Message):
		# Авторизация пользователя.
		User = Users.auth(Message.from_user)

		# Если пользователь уже загружает видео.
		if User.get_property("is_downloading"):
			# Отправка сообщения: загрузка уже идёт.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы уже скачиваете видеоролик."
			)

		# Если удалось опознать ссылку.
		elif urlparse(Message.text).scheme:
			# Отправка сообщения: идёт получение данных.
			SendedMessage = Bot.send_message(
				chat_id = Message.chat.id,
				text = "Идёт получение данных..."
			)
			# Парсинг данных для доступа видео.
			Site = StorageBox.parse_site_name(Message.text)
			VideoID = StorageBox.parse_video_id(Site, Message.text)
			# Попытка получения сохранённых данных.
			Info = StorageBox.get_info(Site, VideoID)
			# Если локальные данные не найдены, запросить новые.
			if not Info: Info = Downloader.get_info(Message.text)

			# Если получение данных успешно.
			if Info:
				# Сохранение данных видео.
				StorageBox.save_info(Site, VideoID, Info)
				# Установка временных свойств.
				User.set_temp_property("link", Message.text)
				User.set_temp_property("site", Site)
				User.set_temp_property("video_id", Info["id"])
				# Удаление сообщения: идёт получение данных.
				Bot.delete_message(message_id = SendedMessage.id, chat_id = Message.chat.id)
				# Отправка меню выбора формата.
				SendFormatSelector(Bot, Message.chat.id, Info)

			else:
				# Редактирование сообщения: не удалось найти видео.
				Bot.edit_message_text(
					message_id = SendedMessage.id,
					chat_id = Message.chat.id,
					text = "Мне не удалось обнаружить видео по этой ссылке."
				)

		else:
			# Отправка сообщения: не удалось распознать ссылку.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "Ваше сообщение не является ссылкой. Попробуйте ещё раз."
			)

	#==========================================================================================#
	# >>>>> ОБРАБОТКА INLINE-КНОПОК <<<<< #
	#==========================================================================================#

	# Обработка Inline-кнопки: скачивание аудио.
	@Bot.callback_query_handler(func = lambda Callback: Callback.data == "download_audio")
	def InlineButton(Call: types.CallbackQuery):
		# Авторизация пользователя.
		User = Users.auth(Call.from_user)
		# Ответ на запрос.
		Bot.answer_callback_query(Call.id)
		# Удаление сообщения.
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		# Блокировка множественной загрузки.
		User.set_property("is_downloading", True)
		# Получение данных.
		Link = User.get_property("link")
		VideoID = User.get_property("video_id")
		Quality = "audio"
		Site = User.get_property("site")
		Compression = User.get_property("compression")
		# Попытка найти файл в хранилище.
		FileMessageID = StorageBox.get_file_message_id(Site, VideoID, Quality, Compression)

		# Если файл уже есть в хранилище.
		if FileMessageID:
			# Пересылка сообщения c файлом.
			Bot.copy_message(Call.message.chat.id, Call.message.chat.id, FileMessageID, caption = "")

		else:
			# Отправка сообщения: скачивание аудио.
			SendedMessage = Bot.send_message(
				chat_id = Call.message.chat.id,
				text = "⏳ Скачиваю аудио..."
			)
			# Скачивание аудио.
			Result = Downloader.download_audio(Link, f"Temp/{User.id}/", f"{VideoID}.m4a")

			# Если скачивание успешно.
			if Result:
				# Редактирование сообщения: выгрузка аудио.
				Bot.edit_message_text(
					chat_id = Call.message.chat.id,
					message_id = SendedMessage.id,
					text = "✅ Аудио скачано.\n⏳ Выгружаю аудио в Telegram..."
				)
				# Запуск выгрузки файла.
				Result = StorageBox.upload_file(User.id, Site, f"{VideoID}.m4a", Quality, Compression)

				# Если выгрузка успешна.
				if Result:
					# Редактирование сообщения: скачивание аудио.
					Bot.edit_message_text(
						chat_id = Call.message.chat.id,
						message_id = SendedMessage.id,
						text = "✅ Аудио скачано.\n✅ Аудио загружено в Telegram.\n⏳ Отправляю..."
					)
					# Ожидание обработки файла.
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression)

					# Если обработка успешна.
					if Result:
						# Пересылка сообщения c файлом.
						Bot.copy_message(Call.message.chat.id, Call.message.chat.id, Result, caption = "")
						# Редактирование сообщения: не удалось отправить файл.
						Bot.edit_message_text(
							chat_id = Call.message.chat.id,
							message_id = SendedMessage.id,
							text = "✅ Аудио скачано.\n✅ Аудио загружено в Telegram.\n✅ Отправлено."
						)

					else:
						# Редактирование сообщения: не удалось отправить файл.
						Bot.edit_message_text(
							chat_id = Call.message.chat.id,
							message_id = SendedMessage.id,
							text = "✅ Аудио скачано.\n✅ Аудио загружено в Telegram.\n❌ Не удалось отправить аудио."
						)

				else:
					# Редактирование сообщения: скачивание аудио.
					Bot.edit_message_text(
						chat_id = Call.message.chat.id,
						message_id = SendedMessage.id,
						text = "✅ Аудио скачано.\n❌ Не удалось загрузить аудио в Telegram."
					)

			else:
				# Редактирование сообщения: скачивание аудио.
				Bot.edit_message_text(
					chat_id = Call.message.chat.id,
					message_id = SendedMessage.id,
					text = "❌ Не удалось скачать аудио."
				)

		# Разблокировка загрузки и очистка временных свойств.
		User.set_property("is_downloading", False)
		User.clear_temp_properties()

	# Обработка Inline-кнопки: скачивание видео.
	@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("download_video_"))
	def InlineButton(Call: types.CallbackQuery):
		# Авторизация пользователя.
		User = Users.auth(Call.from_user)
		# Ответ на запрос.
		Bot.answer_callback_query(Call.id)
		# Удаление сообщения.
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		# Блокировка множественной загрузки.
		User.set_property("is_downloading", True)
		# Получение данных.
		Query = Call.data.replace("download_video_", "")
		Link = User.get_property("link")
		VideoID = User.get_property("video_id")
		Quality = Query.split("_")[0]
		FormatID = Query.split("_")[1]
		Site = User.get_property("site")
		Compression = User.get_property("compression")
		# Попытка найти файл в хранилище.
		FileMessageID = StorageBox.get_file_message_id(Site, VideoID, Quality, Compression)

		# Если файл уже есть в хранилище.
		if FileMessageID:
			# Пересылка сообщения c файлом.
			Bot.copy_message(Call.message.chat.id, Call.message.chat.id, FileMessageID, caption = "")

		else:
			# Отправка сообщения: скачивание видео.
			SendedMessage = Bot.send_message(
				chat_id = Call.message.chat.id,
				text = "⏳ Скачиваю видео..."
			)
			# Скачивание видео.
			Result = Downloader.download_video(Link, f"Temp/{User.id}/", f"{VideoID}.mp4", FormatID)

			# Если скачивание успешно.
			if Result:
				# Редактирование сообщения: выгрузка видео.
				Bot.edit_message_text(
					chat_id = Call.message.chat.id,
					message_id = SendedMessage.id,
					text = "✅ Видео скачано.\n⏳ Выгружаю видео в Telegram..."
				)
				# Запуск выгрузки файла.
				Result = StorageBox.upload_file(User.id, Site, f"{VideoID}.mp4", Quality, Compression)

				# Если выгрузка успешна.
				if Result:
					# Редактирование сообщения: скачивание видео.
					Bot.edit_message_text(
						chat_id = Call.message.chat.id,
						message_id = SendedMessage.id,
						text = "✅ Видео скачано.\n✅ Видео загружено в Telegram.\n⏳ Отправляю..."
					)
					# Ожидание обработки файла.
					Result = StorageBox.wait_file_uploading(Site, VideoID, Quality, Compression)

					# Если обработка успешна.
					if Result:
						# Пересылка сообщения c файлом.
						Bot.copy_message(Call.message.chat.id, Call.message.chat.id, Result, caption = "")
						# Редактирование сообщения: не удалось отправить файл.
						Bot.edit_message_text(
							chat_id = Call.message.chat.id,
							message_id = SendedMessage.id,
							text = "✅ Видео скачано.\n✅ Видео загружено в Telegram.\n✅ Отправлено."
						)

					else:
						# Редактирование сообщения: не удалось отправить файл.
						Bot.edit_message_text(
							chat_id = Call.message.chat.id,
							message_id = SendedMessage.id,
							text = "✅ Видео скачано.\n✅ Видео загружено в Telegram.\n❌ Не удалось отправить видео."
						)

				else:
					# Редактирование сообщения: скачивание видео.
					Bot.edit_message_text(
						chat_id = Call.message.chat.id,
						message_id = SendedMessage.id,
						text = "✅ Видео скачано.\n❌ Не удалось загрузить видео в Telegram."
					)

			else:
				# Редактирование сообщения: скачивание видео.
				Bot.edit_message_text(
					chat_id = Call.message.chat.id,
					message_id = SendedMessage.id,
					text = "❌ Не удалось скачать видео."
				)

		# Разблокировка загрузки и очистка временных свойств.
		User.set_property("is_downloading", False)
		User.clear_temp_properties()

	#==========================================================================================#
	# >>>>> ОБРАБОТКА ФАЙЛОВ <<<<< #
	#==========================================================================================#

	# Обработка файла.				
	@Bot.message_handler(content_types=["audio", "document", "video"])
	def File(Message: types.Message):
		
		# Если доверенный аккаунт прислал видео.
		if Message.from_user.id in Settings["trusted_sources_id"]: 
			# Парсинг данных файла.
			FileData = Message.caption.split("\n")
			Site = FileData[0]
			VideoID = FileData[1]
			Quality = FileData[2]
			Compression = True if FileData[3].endswith("on") else False
			# Регистрация файла.
			StorageBox.register_file(Site, VideoID, Quality, Compression, Message.id)
		
	# Запуск обработки запросов Telegram.
	Bot.infinity_polling()