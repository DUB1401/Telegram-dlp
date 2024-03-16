from dublib.Methods import ReadJSON, WriteJSON
from telethon.sync import TelegramClient

import shutil
import os

class MediaCore:
	"""Хранилище медиа-файлов Telegram."""
	
	def __init__(self, bot_name: str | None = None, data_path: str = "Data"):
		"""
		Хранилище медиа-файлов Telegram.
			bot_name – идентификационное имя бота, которому будут отправляться файлы;
			data_path — директория хранения данных хранилища.
		"""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__DataPath = data_path
		self.__Client = None
		self.__Bot = bot_name
		
	def authorizate(self):
		"""Выполняет авторизацию аккаунта и инициализацию сессии."""
		
		# Чтение данных сессии.
		SessionData = ReadJSON(self.__DataPath + "/Session.json")
		# Инициализция и подключение клиента.
		self.__Client = TelegramClient(self.__DataPath + "/Account.session", SessionData["api-id"], SessionData["api-hash"], system_version = "4.16.30-vxCUSTOM")
		self.__Client.connect()
		
	def close(self):
		"""Завершает сессию."""

		# Отключение и обнуление клиента.
		self.__Client.disconnect()
		self.__Client = None

	def dump(self, path: str, user_id: int, compression: bool = True):
		"""
		Загружает файл на сервера Telegram.
		"""

		# Отправка файла.
		self.__Client.send_file(self.__Bot, path, caption = str(user_id), part_size_kb = 512, force_document = not compression)
		
	def set_session(self, path: str, api_id: int, api_hash: str) -> bool:
		"""
		Устанавливает файл сессии в Telegram для авторизации пользователя.
			path — путь к файлу сессии Telegram.
		"""
		
		# Состояние: успешна ли установка.
		IsSuccess = False
		
		# Если файл существует и имеет формат сессии Telethon.
		if os.path.exists(path) and path.endswith(".session"):
			# Если существует файл сессии в корневом каталоге, удалить его.
			if os.path.exists(self.__DataPath + "/Account.session"): os.remove(self.__DataPath + "/Account.session")
			# Копирование файла сессии.
			shutil.copy2(path, "Data/Account.session")
			# Запись данных сессии.
			WriteJSON(self.__DataPath + "/Session.json", {"api-id": int(api_id), "api-hash": api_hash})
			# Переключение состояния.
			IsSuccess = True
		
		else:
			# Выброс исключения.
			raise FileNotFoundError(f"Unable to open session file: \"{path}\".")
		
		return IsSuccess