from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.CLI.StyledPrinter import StyledPrinter, Styles
from dublib.Methods.JSON import ReadJSON, WriteJSON
from telethon.sync import TelegramClient

import os

class TelethonUser:
	"""Имитатор пользователя."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	def client(self) -> TelegramClient:
		"""Пользовательский клиент."""

		return self.__Client

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict):
		"""
		Имитатор пользователя.
			settings – глобальные настройки.
		"""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Пользовательский клиент.
		self.__Client = None
		# Глобальные настройки.
		self.__Settings = settings.copy()

	def initialize(self, logging: bool = True) -> TelegramClient | None:
		"""
		Инициализирует пользователя.
			logging – указывает, следует ли выводить в консоль дополнительные данные.
		"""

		try:
			# Чтение данных сессии.
			SessionData = ReadJSON("Data/Account.json")
			# Инициализция и подключение клиента.
			self.__Client = TelegramClient("Data/Account.session", SessionData["api_id"], SessionData["api_hash"], system_version = "4.16.30-vxCUSTOM")
			self.__Client.connect()

		except Exception as ExceptionData:
			# Если включён вывод в консоль, вывести ошибку.
			if logging: StyledPrinter(f"ERROR: {ExceptionData}", text_color = Styles.Colors.Red)

		return self.__Client

	def login(self, phone_number: str, api_id: int | str, api_hash: str, logging: bool = True) -> bool:
		"""
		Выполняет авторизацию пользователя в системе.
			phone_number – номер мобильного телефона;
			api_id – идентификатор доступа к API пользователя;
			api_hash – хеш доступа к API пользователя;
			logging – указывает, следует ли выводить в консоль дополнительные данные.
		"""

		# Временный клиент для регистрации.
		Client = None
		# Хеш авторизации клиента.
		Hash = None
		# Состояние: успешна ли авторизация.
		IsSucess = False

		try:
			# Преобразование типов.
			api_id = int(api_id)
			# Инициализация клиента и подключение.
			Client = TelegramClient("Account", api_id, api_hash, system_version = "4.16.30-vxCUSTOM")
			Client.connect()
			
			# Если аккаунт не авторизован.
			if not Client.is_user_authorized():
				# Отправка кода 2FA.
				Hash = Client.sign_in(phone_number).phone_code_hash
				# Запрос кода у пользователя.
				Code = input("Enter protection code from Telegram application: ")
				# Вход с кодом.
				Client.sign_in(phone_number, Code, phone_code_hash = Hash)
				
			# Если клиент авторизован.
			if Client.is_user_authorized():
				# Отключение и обнуление клиента и хеша.
				Client.disconnect()
				Client = None
				Hash = None
				# Перемещение файла сессии для сохранности.
				os.replace("Account.session", "Data/Account.session")
				# Сохранение данных сессии.
				WriteJSON("Data/Account.json", {"phone_number": phone_number, "api_id": api_id, "api_hash": api_hash})
				# Переключение состояния.
				IsSucess = True
				# Если включён вывод в консоль, вывести сообщение об успешном входе.
				if logging: StyledPrinter("Authorization successful.", text_color = Styles.Colors.Green)
			
		except Exception as ExceptionData:
			# Если включён вывод в консоль, вывести ошибку.
			if logging: StyledPrinter(f"ERROR: {ExceptionData}", text_color = Styles.Colors.Red)
			
		return IsSucess
	
	def upload_file(self, user_id: int, site: str, filename: str, quality: str, compression: bool) -> bool:
		"""
		Выгружает файл в Telegram.
			user_id – идентификатор пользователя;
			site – название сайта;
			filename – название файла;
			quality – качество видео;
			compression – указывает, нужно ли использовать сжатие.
		"""

		# Состояние: отправлен ли файл.
		IsSuccess = False
		
		try:
			# Идентификатор видео.
			VideoID = filename[:-4]
			# Приведение компрессии из логики в строку.
			Compression = "compression: on" if compression else "compression: off"
			# Подпись сообщения.
			Caption = f"{site}\n{VideoID}\n{quality}\n{Compression}"
			# Отправка файла.
			self.__Client.send_message(self.__Settings["bot_name"], message = Caption, file = f"Temp/{user_id}/{filename}", force_document = not compression)
			# Удаление файлов и директории пользователя.
			RemoveDirectoryContent(f"Temp/{user_id}")
			os.rmdir(f"Temp/{user_id}")
			# Переключение состояния.
			IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)

		return IsSuccess