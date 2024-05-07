from dublib.Methods import ReadJSON, WriteJSON
from telethon.sync import TelegramClient

import shutil
import sys
import os

class MediaCore:
	"""Хранилище медиа-файлов Telegram."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetFilename(self, user_id: int) -> str | None:
		"""
		Возвращает имя файла в директории пользователя, подготовленного к выгрузке.
			user_id – ID пользователя.
		"""

		# Получение имён файлов в директории пользователя.
		Files = os.listdir(f"Files/{user_id}")

		# Для каждого файла.
		for File in Files:
			# Если файл не является описательным JSON, вернуть его имя.
			if not File.endswith(".json"): return File

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, settings: dict, data_path: str = "Data"):
		"""
		Хранилище медиа-файлов Telegram.
			settings – словарь глобальных настроек;
			data_path — директория хранения данных.
		"""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = settings.copy()
		# Путь к хранилищу.
		self.__DataPath = data_path
		# Клиент пользователя Telegram.
		self.__Client = None
		
	def authorizate(self):
		"""Выполняет авторизацию аккаунта и инициализацию сессии."""
		
		# Чтение данных сессии.
		SessionData = ReadJSON(self.__DataPath + "/Session.json")
		# Инициализция и подключение клиента.
		self.__Client = TelegramClient(self.__DataPath + "/Account.session", SessionData["api-id"], SessionData["api-hash"], system_version = "4.16.30-vxCUSTOM")
		self.__Client.connect()
		
	def check_file_on_storage(self, domain: str, file_id: str, resolution: str, compression: bool) -> int | None:
		"""
		Проверяет, находится ли файл на сервере.
			domain – домен сайта-источника;
			file_id – ID файла;
			resolution – разрешение файла;
			compression – состояние: используется ли сжатие.
		"""

		# Если файл определён в хранилище.
		if os.path.exists(f"Data/Storage/{domain}/{file_id}.json"):
			# Чтение данных файла.
			Data = ReadJSON(f"Data/Storage/{domain}/{file_id}.json")
			# Ключ доступа к данным файлов.
			CompressionKey = "compressed" if compression else "not-compressed"
			# Если расширение уже загружено, вернуть ID сообщения.
			if resolution in Data[CompressionKey].keys(): return Data[CompressionKey][resolution]

	def close(self):
		"""Завершает сессию."""

		# Отключение и обнуление клиента.
		self.__Client.disconnect()
		self.__Client = None
		
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

	def upload(self, user_id: int, compression: bool = True):
		"""Загружает файл на сервера Telegram."""

		# Чтение файла описания видео.
		Description = ReadJSON(f"Files/{user_id}/description.json")
		# Если каталога домена не существует, создать.
		if not os.path.exists("Data/Storage/" + Description["domain"]): os.makedirs("Data/Storage/" + Description["domain"])

		# Если файла определений не существует.
		if not os.path.exists("Data/Storage/" + Description["domain"] + "/" + Description["id"] + ".json"):
			# Создание файла определений.
			WriteJSON("Data/Storage/" + Description["domain"] + "/" + Description["id"] + ".json", {"compressed": {}, "not-compressed": {}})

		# Чтение файла определений.
		StorageData = ReadJSON("Data/Storage/" + Description["domain"] + "/" + Description["id"] + ".json")
		# Выбор ключа доступа.
		CompressionKey = "compressed" if compression else "not-compressed"
		# Создание подписи файла.
		Caption = str(user_id) + "\n" + Description["domain"] + "\n" + Description["id"] + "\n" + Description["resolution"]
		# Отправка файла.
		Message = self.__Client.send_message(self.__Settings["bot-name"], Caption, file = f"Files/{user_id}/" + self.__GetFilename(user_id), force_document = not compression)
		# Запись ID отправленного сообщения.
		StorageData[CompressionKey][Description["resolution"]] = None
		# Запись данных в хранилище.
		WriteJSON("Data/Storage/" + Description["domain"] + "/" + Description["id"] + ".json", StorageData)
		
	def dump(self, user_id: str, compression: bool) -> int:
		"""
		Запускает процесс выгрузки файла на сервер.
			user_id – ID пользователя, запросившего загрузку файла;
			compression – состояние: включено ли сжатие видео.
		"""

		# Определения исполняемых команд.
		Commands = {
			 "linux": "python3." + str(sys.version_info[1]) + f" main.py dump {user_id}",
			 "win32": f"python main.py dump {user_id}"
		}
		# Расчёт лимита.
		Limit = 3800000000 if self.__Settings["premium"] else 1900000000
		# Код завершения.
		ExitCode = 1
		
		try:
			
			# Если размер файла не превышает лимит.
			if os.path.getsize(f"Files/{user_id}/" + self.__GetFilename(user_id)) < Limit:
				# Выполнение загрузки.
				ExitCode = os.system(Commands[sys.platform] + (" -compress" if compression else ""))
		
			else:
				# Изменение кода.
				ExitCode = -1
			
		except: pass
		
		return ExitCode