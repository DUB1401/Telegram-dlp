from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.CLI.TextStyler import TextStyler, Styles

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

	def __init__(self, bot_name: dict):
		"""
		Имитатор пользователя.
			bot_name – текстовый идентификатор бота.
		"""
		
		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Client = None
		self.__BotName = bot_name

	def initialize(self) -> TelegramClient:
		"""Инициализирует пользователя."""

		SessionData = ReadJSON("Data/Account.json")
		self.__Client = TelegramClient("Data/Account.session", SessionData["api_id"], SessionData["api_hash"], system_version = "4.16.30-vxCUSTOM")
		self.__Client.connect()

		return self.__Client

	def login(self, phone_number: str, api_id: int | str, api_hash: str, logging: bool = True) -> bool:
		"""
		Выполняет авторизацию пользователя в системе.
			phone_number – номер мобильного телефона;
			api_id – идентификатор доступа к API пользователя;
			api_hash – хеш доступа к API пользователя;
			logging – указывает, следует ли выводить в консоль дополнительные данные.
		"""

		Client = None
		Hash = None
		IsSucess = False

		try:
			api_id = int(api_id)
			Client = TelegramClient("Account", api_id, api_hash, system_version = "4.16.30-vxCUSTOM")
			Client.connect()
			
			if not Client.is_user_authorized():
				Hash = Client.sign_in(phone_number).phone_code_hash
				Code = input("Enter protection code from Telegram application: ")
				Client.sign_in(phone_number, Code, phone_code_hash = Hash)
				
			if Client.is_user_authorized():
				Client.disconnect()
				Client = None
				Hash = None
				os.replace("Account.session", "Data/Account.session")
				WriteJSON("Data/Account.json", {"phone_number": phone_number, "api_id": api_id, "api_hash": api_hash})
				IsSucess = True
				if logging: TextStyler("Authorization successful.", text_color = Styles.Colors.Green).print()
			
		except Exception as ExceptionData:
			if logging: TextStyler(f"ERROR: {ExceptionData}", text_color = Styles.Colors.Red).print()
			
		return IsSucess
	
	def upload_file(self, user_id: int, site: str, filename: str, quality: str, compression: bool, recoding: bool, watermarked: bool, name: str | None = None) -> bool:
		"""
		Выгружает файл в Telegram.
			user_id – идентификатор пользователя;
			site – название сайта;
			filename – название файла;
			quality – качество видео;
			compression – указывает, нужно ли использовать сжатие;
			recoding – указывает, перекодирован ли формат в стандартный;
			watermarked – указывает, имеет ли видео водяной знак;
			name – новое название файла.
		"""

		IsSuccess = False
		
		try:
			VideoID = filename[:(len(filename.split(".")[-1]) + 1) * -1]
			Compression = "compression: on" if compression else "compression: off"
			Recoding = "recoding: on" if recoding else "recoding: off"
			Watermarked = "watermarked: on" if watermarked else "watermarked: off"
			Caption = f"{site}\n{VideoID}\n{quality}\n{Compression}\n{Recoding}\n{Watermarked}"

			if name:
				if quality != "audio": name += ".mp4"
				os.rename(f"Temp/{user_id}/{filename}", f"Temp/{user_id}/{name}")

			else:
				name = filename

			self.__Client.send_message(self.__BotName, message = Caption, file = f"Temp/{user_id}/{name}", force_document = not compression)
			RemoveDirectoryContent(f"Temp/{user_id}")
			os.rmdir(f"Temp/{user_id}")
			IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)

		return IsSuccess