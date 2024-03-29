﻿from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON
from dublib.Terminalyzer import ArgumentsTypes, Command, Terminalyzer
from dublib.StyledPrinter import StyledPrinter, Styles
from Source.Functions import BuildMenu, UpdatePremium
from Source.VideoManager import VideoManager
from Source.Registrator import Registrator
from Source.MediaCore import MediaCore
from Source.Users import UsersManager
from urllib.parse import urlparse
from telebot import types

import telebot

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Files"])

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
COM_dump.add_argument(ArgumentsTypes.Number, important = True)
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
	MediaCoreObject = MediaCore(Settings["bot-name"])
	MediaCoreObject.authorizate()
	MediaCoreObject.dump(CommandDataStruct.arguments[0], CommandDataStruct.arguments[1], Compression)
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
	VideoManagerObject = VideoManager()
	UsersManagerObject = UsersManager()
	
	# Обработка команды: about.
	@Bot.message_handler(commands = ["about"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		# Отправка сообщения: информация о проекте.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "*Telegram\-dlp* является Open Source проектом под лицензией Apache 2\.0 за авторством [@DUB1401](https://github.com/DUB1401)\ и использует библиотеку [yt\-dlp](https://github.com/yt-dlp/yt-dlp)\. Исходный код и документация доступны в [этом](https://github.com/DUB1401/Telegram-dlp) репозитории\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True
		)
	
	# Обработка команды: start.
	@Bot.message_handler(commands = ["start"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		# Изменение статуса загрузки.
		UsersManagerObject.set_user_value(User.id, "downloading", False)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			chat_id = Message.chat.id,
			text = "Здравствуйте\!\n\nЯ бот, помогающий скачивать видео\. Со списком поддерживаемых источиков можно ознакомиться [здесь](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)\.\n\nОтправьте мне ссылку на видео для начала работы\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True,
			reply_markup = BuildMenu(User)
		)
		
	# Обработка текстовых сообщений.
	@Bot.message_handler(content_types = ["text"])
	def Link(Message: types.Message):
		# Авторизация пользователя.
		User = UsersManagerObject.auth(Message.from_user)
		
		# Обработка кнопки: отключение сжатия.
		if Message.text == "🔴 Отключить сжатие":
			# Отключение компрессии.
			UsersManagerObject.set_user_value(User.id, "compression", False)
			# Отправка сообщения: сжатие видео отключено.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "*⚙️  Настройки*\n\nСжатие видео отключено\.",
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User)
			)
			
		# Обработка кнопки: включение сжатия.
		elif Message.text == "🟢 Включить сжатие":
			# Включение компрессии.
			UsersManagerObject.set_user_value(User.id, "compression", True)
			# Отправка сообщения: сжатие видео отключено.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "*⚙️  Настройки*\n\nСжатие видео включено\.",
				parse_mode = "MarkdownV2",
				reply_markup = BuildMenu(User)
			)
			
		else:
		
			# Если сообщение является ссылкой.
			if urlparse(Message.text).scheme:
				
				# Если пользователь в данный момент не загружает файл.
				if UsersManagerObject.get_user(Message.from_user.id).downloading == False:
					# Отправка сообщения: видео скачивается.
					MessageID = Bot.send_message(
						chat_id = Message.chat.id,
						text = "*⏳  Загрузка*\n\nВидео скачивается\.\.\.",
						parse_mode = "MarkdownV2"
					).id
					# Блокировка загрузки.
					UsersManagerObject.set_user_value(User.id, "downloading", True)
					# Загрузка видео.
					ExitCode = VideoManagerObject.download(Message.text, Message.from_user.id, Settings["original-filenames"])
				
					# Если скачивание успешно.
					if ExitCode != None:
						# Редактирование сообщения: видео загружается на сервер.
						Bot.edit_message_text(
							text = "*⏳  Загрузка*\n\nВидео загружается на сервер Telegram\.\.\.",
							chat_id = Message.chat.id,
							message_id = MessageID,
							parse_mode = "MarkdownV2"
						)
						# Выбор имени файла: оригинальное или ID.
						Filename = ExitCode["title"].strip() if Settings["original-filenames"] else ExitCode["id"]
						# Загрузка видео на сервера Telegram.
						ExitCode = VideoManagerObject.dump(Filename, Message.from_user.id, User.compression, premium = Settings["premium"])
				
						# Если загрузка успешна.
						if ExitCode == 0:
							# Редактирование сообщения: видео загружено на сервер.
							Bot.edit_message_text(
								text = "*⏳  Загрузка*\n\nВидео загружено\. Идёт отправка\.\.\.",
								chat_id = Message.chat.id,
								message_id = MessageID,
								parse_mode = "MarkdownV2"
							)
					
						elif ExitCode == -1:
							# Расчёт лимита.
							Limit = 4 if Settings["premium"] else 2
							# Редактирование сообщения: видео превышает лимит.
							Bot.edit_message_text(
								text = f"*❗  Ошибка*\n\nВидео слишком большое для загрузки на сервер\. Telegram устанавливает лимит в {Limit} GB.",
								chat_id = Message.chat.id,
								message_id = MessageID,
								parse_mode = "MarkdownV2"
							)
					
						else:
							# Редактирование сообщения: не удалось загрузить видео.
							Bot.edit_message_text(
								text = "*❗  Ошибка*\n\nМне не удалось загрузить ваше видео на сервер Telegram\.",
								chat_id = Message.chat.id,
								message_id = MessageID,
								parse_mode = "MarkdownV2"
							)
		
					else:
						# Редактирование сообщения: не удалось скачать видео.
						Bot.edit_message_text(
							text = "*❗  Ошибка*\n\nМне не удалось скачать ваше видео\.",
							chat_id = Message.chat.id,
							message_id = MessageID,
							parse_mode = "MarkdownV2"
						)
					
					# Разблокировка загрузки.
					UsersManagerObject.set_user_value(User.id, "downloading", False)
					
				else:
					# Отправка сообщения: пользователь уже скачивает видео.
					Bot.send_message(
						chat_id = Message.chat.id,
						text = "*❗  Ошибка*\n\nВы уже загружаете одно видео\.",
						parse_mode = "MarkdownV2"
					)
			
			else:
				# Отправка сообщения: не удалось найти ссылку.
				Bot.send_message(
					chat_id = Message.chat.id,
					text = "*❗  Ошибка*\n\nМне не удалось найти ссылку в вашем сообщении\.",
					parse_mode = "MarkdownV2",
					reply_markup = BuildMenu(User)
				)
	
	# Обработка видео (со сжатием и без сжатия).					
	@Bot.message_handler(content_types=["document", "video"])
	def Video(Message: types.Message):
		
		# Если доверенный аккаунт прислал видео.
		if Message.from_user.id == Settings["trusted-source-id"]: 
			# Обновление данных о Premium-статусе.
			UpdatePremium(Settings, Message.from_user)
			# Пересылка сообщения.
			Bot.copy_message(Message.caption, Message.chat.id, Message.id, caption = "")
		
	# Запуск обработки запросов Telegram.
	Bot.infinity_polling()