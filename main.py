from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON, RemoveFolderContent, WriteJSON
from Source.Functions import BuildMenu, BuildResolutions, UpdatePremium
from dublib.Terminalyzer import ArgumentsTypes, Command, Terminalyzer
from dublib.StyledPrinter import StyledPrinter, Styles
from dublib.TelebotUtils import UsersManager
from Source.Registrator import Registrator
from Source.MessageBox import MessageBox
from Source.MediaCore import MediaCore
from urllib.parse import urlparse
from Source.YtDlp import YtDlp
from telebot import types
from time import sleep

import telebot
import os

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Data/Storage", "Files"])

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

# Создание команды: dump.
COM_dump = Command("dump")
COM_dump.add_argument(ArgumentsTypes.All, important = True)
COM_dump.add_flag_position(["compress"])
CommandsList.append(COM_dump)

# Создание команды: login.
COM_login = Command("login")
COM_login.add_argument(ArgumentsTypes.All, important = True)
COM_login.add_argument(ArgumentsTypes.All, important = True)
COM_login.add_argument(ArgumentsTypes.All, important = True)
CommandsList.append(COM_login)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд. 
CommandDataStruct = CAC.check_commands(CommandsList)

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: dump.
if CommandDataStruct != None and "dump" == CommandDataStruct.name:
	# Состояние: использовать ли компрессию.
	Compression = True if "compress" in CommandDataStruct.flags else False
	# Инициализация медиа-ядра.
	MediaCoreObject = MediaCore(Settings)
	MediaCoreObject.authorizate()
	MediaCoreObject.upload(CommandDataStruct.arguments[0], Compression)
	MediaCoreObject.close()
	
# Обработка команды: login.
elif CommandDataStruct != None and "login" == CommandDataStruct.name:
	# Инициализация регистратора.
	RegistratorObject = Registrator()
	# Регистрация без кода.
	Result = RegistratorObject.login(CommandDataStruct.arguments[0], CommandDataStruct.arguments[1], CommandDataStruct.arguments[2])
	# Если запрошен код, произвести авторизацию с кодом.
	if Result == -1: Result = RegistratorObject.login(CommandDataStruct.arguments[0], CommandDataStruct.arguments[1], CommandDataStruct.arguments[2], input("Enter security code: "))

	# Если регистрация успешна.
	if Result == 0:
		# Вывод в консоль: аккаунт успешно добавлен.
		StyledPrinter("Account successfully logined.", text_color = Styles.Colors.Green)
		
	else:
		# Вывод в консоль: ошибка добавления аккаунта.
		StyledPrinter("Unable to login account.", text_color = Styles.Colors.Red)
	
# Запуск Telegram бота.
else:
	# Токен для работы определенного бота телегамм.
	Bot = telebot.TeleBot(Settings["token"])
	# Инициализация интерфейсов.
	VideoManagerObject = YtDlp("yt-dlp", proxy = Settings["proxy"] if Settings["proxy"] else None)
	MediaCoreObject = MediaCore(Settings)
	UsersManagerObject = UsersManager("Data/Users")
	MessageBoxObject = MessageBox()
	
	# Обработка команды: about.
	@Bot.message_handler(commands = ["about"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		# Отправка сообщения: информация о проекте.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = MessageBoxObject.get("about", language = User.language),
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)
	
	# Обработка команды: start.
	@Bot.message_handler(commands = ["start"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		User.create_property("compression", True)
		User.create_property("video", None, True)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = MessageBoxObject.get("hello", language = User.language),
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True,
			reply_markup = BuildMenu(User, MessageBoxObject)
		)
		
	# Обработка текстовых сообщений.
	@Bot.message_handler(content_types = ["text"])
	def Link(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		
		# Обработка кнопки: отключение сжатия.
		if Message.text == MessageBoxObject.get("button-compression-off", language = User.language):
			# Отключение компрессии.
			User.set_property("compression", False)
			# Отправка сообщения: сжатие видео отключено.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = MessageBoxObject.get("compression-off", language = User.language),
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User, MessageBoxObject)
			)
			
		# Обработка кнопки: включение сжатия.
		elif Message.text == MessageBoxObject.get("button-compression-on", language = User.language):
			# Включение компрессии.
			User.set_property("compression", True)
			# Отправка сообщения: сжатие видео включено.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = MessageBoxObject.get("compression-on", language = User.language),
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User, MessageBoxObject)
			)
			
		# Если сообщение является ссылкой.
		elif urlparse(Message.text).scheme:
				
			# Если пользователь в данный момент не загружает файл.
			if not User.get_property("video"):
				# Отправка сообщения: получение данных о видео.
				MessageID = Bot.send_message(
					chat_id = Message.chat.id,
					text = MessageBoxObject.get("dumping", "downloading", language = User.language),
					parse_mode = "MarkdownV2"
				).id
				# Получение данных.
				Dump = VideoManagerObject.get_info(Message.text)

				# Если получение описания успешно.
				if Dump != None:
					# Удаление сообщения: получение данных о видео.
					Bot.delete_message(Message.chat.id, MessageID)
					# Получение словаря разрешений.
					Resolutions = VideoManagerObject.get_resolutions(Dump)
					ResolutionsList = list(Resolutions.keys())
					ResolutionsList.reverse()
					# Блокировка загрузки.
					User.set_property("video", {"link": Message.text, "id": Dump["id"], "formats": Resolutions, "domain": Dump["webpage_url_domain"], "dump": Dump})
					# Отправка сообщения: список разрешений.
					MessageID = Bot.send_message(
						chat_id = Message.chat.id,
						text = MessageBoxObject.get("choose-resolution", language = User.language),
						parse_mode = "MarkdownV2",
						reply_markup = BuildResolutions(ResolutionsList)
					).id
					
				else:
					# Редактирование сообщения: не удалось получить данные.
					Bot.edit_message_text(
						text = MessageBoxObject.get("bad-dumping", "error", language = User.language),
						chat_id = Message.chat.id,
						message_id = MessageID,
						parse_mode = "MarkdownV2"
					)				
	
			else:
				# Отправка сообщения: пользователь уже скачивает видео.
				Bot.send_message(
					chat_id = Message.chat.id,
					text = MessageBoxObject.get("already-downloading", "error", language = User.language),
					parse_mode = "MarkdownV2"
				)

		# Если выбрано разрешение.
		elif Message.text.replace("x", "").lstrip("🎬 🎵").isdigit() or "audio only" in Message.text:
			# Отправка сообщения: выбрано разрешение.
			MessageID = Bot.send_message(
				chat_id = Message.chat.id,
				text = MessageBoxObject.get("preparing", language = User.language),
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User, MessageBoxObject)
			).id
			# Отправка сообщения: начато скачивание.
			MessageID = Bot.send_message(
				chat_id = Message.chat.id,
				text = MessageBoxObject.get("downloading", "downloading", language = User.language),
				parse_mode = "MarkdownV2"
			).id
			# Выбранное разрешение.
			Resolution = Message.text.strip("🎬 🎵")
			# Получение данных видео.
			Video = User.get_property("video")
			# Проверка наличия файла на сервере.
			FileOnServerID = MediaCoreObject.check_file_on_storage(Video["domain"], Video["id"], Resolution, User.get_property("compression"))
			
			# Если файл уже был загружен на сервер.
			if FileOnServerID:
				# Пересылка сообщения с видео. 
				Bot.copy_message(Message.chat.id, Settings["trusted-source-id"], FileOnServerID, caption = "")
				# Удаление сообщения: загрузка файла.
				Bot.delete_message(Message.chat.id, MessageID)

			else:
				# Состояние: успешна ли загрузка.
				IsDownloaded = None

				# Если запрошена только аудиодорожка.
				if "audio only" in Message.text:
					# Старт скачивания аудидорожки.
					IsDownloaded = VideoManagerObject.download_audio(Video["link"], f"Files/{User.id}", Video["id"])

				else:
					# Старт скачивания видео.
					IsDownloaded = VideoManagerObject.download_video(Video["link"], f"Files/{User.id}", Video["id"], Video["formats"][Resolution])

				# Если скачивание успешно.
				if IsDownloaded:
					# Сохранение описания.
					WriteJSON(f"Files/{User.id}/description.json", {"link": Video["link"], "id": Video["id"], "domain": Video["domain"], "resolution": Resolution})
					# Редактирование сообщения: видео загружается на сервер.
					Bot.edit_message_text(
						text = MessageBoxObject.get("uploading", "downloading", language = User.language),
						chat_id = Message.chat.id,
						message_id = MessageID,
						parse_mode = "MarkdownV2"
					)
					# Данные видео.
					Dump = User.get_property("video")["dump"]
					# Если папка источника не создана, создать её.
					if not os.path.exists("Data/Storage/" + Dump["webpage_url_domain"]): os.makedirs("Data/Storage/" + Dump["webpage_url_domain"])

					# Если файла определений не существует.
					if not os.path.exists("Data/Storage/" + Dump["webpage_url_domain"] + "/" + Dump["id"] + ".json"):
						# Создание файла определений.
						WriteJSON("Data/Storage/" + Dump["webpage_url_domain"] + "/" + Dump["id"] + ".json", {"compressed": {}, "not-compressed": {}, "dump": Dump})

					# Загрузка видео на сервера Telegram.
					ExitCode = MediaCoreObject.dump(Message.from_user.id, User.get_property("compression"))
					
					# Если загрузка успешна.
					if ExitCode == 0:
						# Редактирование сообщения: видео загружено на сервер.
						Bot.edit_message_text(
							text = MessageBoxObject.get("sended", "downloading", language = User.language),
							chat_id = Message.chat.id,
							message_id = MessageID,
							parse_mode = "MarkdownV2"
						)
				
					elif ExitCode == -1:
						# Расчёт лимита.
						Limit = 4 if Settings["premium"] else 2
						# Редактирование сообщения: видео превышает лимит.
						Bot.edit_message_text(
							text = MessageBoxObject.get("too-large", "error", {"limit": Limit}, language = User.language),
							chat_id = Message.chat.id,
							message_id = MessageID,
							parse_mode = "MarkdownV2"
						)
				
					else:
						# Редактирование сообщения: не удалось загрузить видео.
						Bot.edit_message_text(
							text = MessageBoxObject.get("unable-upload", "error", language = User.language),
							chat_id = Message.chat.id,
							message_id = MessageID,
							parse_mode = "MarkdownV2"
						)

				else:
					# Редактирование сообщения: не удалось скачать видео.
					Bot.edit_message_text(
						text = MessageBoxObject.get("unable-download", "error", language = User.language),
						chat_id = Message.chat.id,
						message_id = MessageID,
						parse_mode = "MarkdownV2"
					)
			
			# Разблокировка загрузки.
			User.set_property("video", None)
		
		else:
			# Отправка сообщения: не удалось найти ссылку.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = MessageBoxObject.get("uploading", "downloading", language = User.language),
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User, MessageBoxObject)
			)
	
	# Обработка аудио.					
	@Bot.message_handler(content_types=["audio"])
	def Video(Message: types.Message):
		
		# Если доверенный аккаунт прислал видео.
		if Message.from_user.id == Settings["trusted-source-id"]: 
			# Обновление данных о Premium-статусе.
			UpdatePremium(Settings, Message.from_user)
			# Аргументы видео.
			Args = Message.caption.split("\n")
			# Файл определений.
			StorageData = None

			# Пока файл не прочитан.
			while not StorageData:

				try:
					# Чтение файла.
					StorageData = ReadJSON("Data/Storage/" + Args[1] + "/" + Args[2] + ".json")

				except: sleep(1)

			# Внесение в реестр ID от лица бота.
			StorageData["compressed"][Args[3]] = Message.id
			StorageData["not-compressed"][Args[3]] = Message.id
			# Запись данных в хранилище.
			WriteJSON("Data/Storage/" + Args[1] + "/" + Args[2] + ".json", StorageData)
			# Пересылка сообщения.
			Bot.copy_message(Args[0], Message.chat.id, Message.id, caption = "")
			# Очитска буферной директории.
			RemoveFolderContent("Files/" + Args[0])

	# Обработка видео (со сжатием и без сжатия).					
	@Bot.message_handler(content_types=["audio", "document", "video"])
	def Video(Message: types.Message):
		
		# Если доверенный аккаунт прислал видео.
		if Message.from_user.id == Settings["trusted-source-id"]: 
			# Обновление данных о Premium-статусе.
			UpdatePremium(Settings, Message.from_user)
			# Аргументы видео.
			Args = Message.caption.split("\n")
			# Выбор ключа доступа.
			CompressionKey = "compressed" if UsersManagerObject.get_user(Args[0]).get_property("compression") else "not-compressed"
			# Файл определений.
			StorageData = None

			# Пока файл не прочитан.
			while not StorageData:

				try:
					# Чтение файла.
					StorageData = ReadJSON("Data/Storage/" + Args[1] + "/" + Args[2] + ".json")

				except: sleep(1)
				
			# Внесение в реестр ID от лица бота.
			StorageData[CompressionKey][Args[3]] = Message.id
			# Запись данных в хранилище.
			WriteJSON("Data/Storage/" + Args[1] + "/" + Args[2] + ".json", StorageData)
			# Пересылка сообщения.
			Bot.copy_message(Args[0], Message.chat.id, Message.id, caption = "")
			# Очитска буферной директории.
			RemoveFolderContent("Files/" + Args[0])
		
	# Запуск обработки запросов Telegram.
	Bot.infinity_polling()