from dublib.Methods.JSON import ReadJSON, WriteJSON
from urllib.parse import urlparse, parse_qs
from time import sleep

import sys
import os

class Storage:
	"""Хранилище данных медиа-файлов."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __SearchFormat(self, data: dict, quality: str, compression: bool) -> int | None:
		"""
		Возвращает индекс формата.
			data – данные видео;
			quality – качество видео;
			compression – использовалось ли сжатие.
		"""

		# Индекс формата.
		FormatIndex = None

		# Для каждого формата видео.
		for Index in range(len(data["video"])):

			# Если формат полностью совпадает.
			if data["video"][Index]["quality"] == quality and data["video"][Index]["compression"] == compression:
				# Сохранение индекса.
				FormatIndex = Index
				# Прерывание цикла.
				break

		return FormatIndex

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, directory: str, venv: bool = True):
		"""
		Хранилище данных медиа-файлов.
			directory – путь к директории хранения;
			venv – указывает, используется ли вирутальная среда Python.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Путь к директории хранения.
		self.__StorageDirectory = directory
		# Состояние: используется ли вирутальная среда Python.
		self.__Venv = venv

	def get_file_message_id(self, site: str, id: str, quality: str, compression: bool) -> int | None:
		"""
		Возвращает идентификатор сообщения с файлом.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке.
		"""

		# Идентификатор сообщения.
		MessageID = None
		# Путь к директории хранения.
		Path = f"{self.__StorageDirectory}/Files/{site}"

		# Если файл существует.
		if os.path.exists(f"{Path}/{id}.json"):
			# Чтение содержимого.
			File = ReadJSON(f"{Path}/{id}.json")

			# Если запрошено аудио.
			if quality == "audio":
				# Получение ID сообщения.
				MessageID = File["audio"]

			else:
				# Поиск формата.
				FormatIndex = self.__SearchFormat(File, quality, compression)
				# Если формат найден, записать ID сообщения.
				if FormatIndex != None: MessageID = File["video"][FormatIndex]["message_id"]

		return MessageID

	def get_info(self, site: str, id: str | None) -> dict | None:
		"""
		Вовзаращает сохранённые данные видео, если поддерживается.
			site – название сайта;
			id – идентификатор видео.
		"""

		# Данные видео.
		Info = None

		# Если удалось определить идентификатор.
		if id:
			# Путь к файлу данных.
			Path = f"{self.__StorageDirectory}/Info/{site}/{id}.json"
			# Если файл существует, прочитать его.
			if os.path.exists(Path): Info = ReadJSON(Path)

		return Info

	def parse_site_name(self, link: str) -> str:
		"""
		Получает название сайта из ссылки.
			link – ссылка.
		"""

		# Название сайта.
		Site = urlparse(link).hostname
		# Обработка альтренативных доменов.
		if Site == "": Site = ""
		
		return Site
	
	def parse_video_id(self, site: str, link: str) -> str | None:
		"""
		Получает идентификатор видео из ссылки, если сохранение данных видео из источника поддерживается.
			site – название сайта;
			link – ссылка.
		"""

		# Идентификатор видео.
		VideoID = None

		# Получение ID видео c YouTube.
		if site == "www.youtube.com":
			# Парсинг строки запроса.
			Query = urlparse(link).query
			Query = parse_qs(Query)
			# Если есть ключ ID видео, записать его значение.
			if "v" in Query.keys(): VideoID = Query["v"][0]
		
		return VideoID

	def register_file(self, site: str, id: str, quality: str, compression: bool, message_id: int):
		"""
		Добавляет видео в хранилище.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			message_id – идентификатор сообщения с файлом.
		"""

		# Путь к директории хранения.
		Path = f"{self.__StorageDirectory}/Files/{site}"
		# Если директория не существует, создать её.
		if not os.path.exists(Path): os.makedirs(Path)
		# Содержимое файла.
		File = None

		# Если файл существует.
		if os.path.exists(f"{Path}/{id}.json"):
			# Чтение содержимого.
			File = ReadJSON(f"{Path}/{id}.json")

		else:
			# Инициализация файла.
			File = {
				"video": [],
				"audio": None
			}

		# Если регистрируется аудио.
		if quality == "audio":
			# Запись идентификатора сообщения с аудио.
			File["audio"] = message_id

		# Если формат видео не найден.
		elif self.__SearchFormat(File, quality, compression) == None:
			# Буфер данных формата.
			Format = {
				"quality": quality,
				"compression": compression,
				"message_id": message_id
			}
			# Запись формата.
			File["video"].append(Format)

		# Сохранение файла.
		WriteJSON(f"{Path}/{id}.json", File)

	def save_info(self, site: str, id: str | None, info: dict):
		"""
		Сохраняет данные видео, если поддерживается.
			site – название сайта;
			id – идентификатор видео;
			info – словарь данных.
		"""

		# Если удалось определить идентификатор.
		if id:
			# Директория сохранения.
			SaveDirectory = f"{self.__StorageDirectory}/Info/{site}"
			# Если директория не существует, создать её.
			if not os.path.exists(SaveDirectory): os.makedirs(SaveDirectory)
			# Сохранение описания.
			WriteJSON(f"{SaveDirectory}/{id}.json", info)

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
		# Минорная версия Python.
		PythonMinorVersion = sys.version_info[1]
		# Преобразование значений в части команды.
		compression = "-c" if compression else ""
		Venv = "source .venv/bin/activate &&" if self.__Venv else ""
		# Запуск выгрузки.
		Result = os.system(f"{Venv} python3.{PythonMinorVersion} main.py upload --user {user_id} --site {site} --file {filename} --quality {quality} {compression}")
		# Если загрузка успешна, переключить состояние.
		if Result == 0: IsSuccess = True

		return IsSuccess
	
	def wait_file_uploading(self, site: str, id: str, quality: str, compression: bool, timeout: int = 30) -> int | None:
		"""
		Ждёт загрузки файла и возвращает идентификатор сообщения с ним.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			timeout – время ожидания в секундах.
		"""

		# Индекс попытки.
		Try = 0
		# Идентификатор сообщения.
		MessageID = None

		# Пока не вышло время или не получен идентификатор.
		while Try < timeout or not MessageID:
			# Инкремент попытки.
			Try += 1
			# Попытка получения идентификатора.
			MessageID = self.get_file_message_id(site, id, quality, compression)
			# Если идентификатор не получен, выждать секунду.
			if not MessageID: sleep(1)

		return MessageID