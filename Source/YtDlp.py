from dublib.Methods.JSON import ReadJSON, WriteJSON
from urllib.parse import urlparse, parse_qs

import subprocess
import json
import sys
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __FilterInfo(self, info: dict) -> dict:
		"""
		Оставляет только основные форматы видео.
			info – словарь описания видео.
		"""

		# Буфер обработки.
		Buffer = info.copy()
		# Очистка форматов.
		Buffer["formats"] = list()
		
		# Для каждого формата.
		for Format in info["formats"]:
			# Если формат упакован в MP4 и содержит аудиодорожку, записать его.
			if Format["ext"] == "mp4": Buffer["formats"].append(Format)

		return Buffer

	def __ProcessLink(self, link: str) -> dict | None:
		"""
		Обрабатывает ссылку в попытке получить сохранённые данные видео.
			link – ссылка.
		"""

		# Данные видео.
		Dump = None

		# Если ссылка относится к мобильному YouTube.
		if "youtu.be" in link:
			# Парсинг ссылки.
			VideoID = link.split("/")[-1]
			# Если локальное описание существует, подгрузить его.
			if os.path.exists(f"Data/Storage/youtube.com/{VideoID}.json"): Dump = ReadJSON(f"Data/Storage/youtube.com/{VideoID}.json")["dump"]

		# Если ссылка относится к YouTube.
		if "youtube.com" in link:
			# Парсинг ссылки.
			ParsedLink = urlparse(link)
			Query = parse_qs(ParsedLink.query)
			if "v" in Query.keys(): VideoID = str(Query["v"][0])
			# Если локальное описание существует, подгрузить его.
			if "v" in Query.keys() and os.path.exists(f"Data/Storage/youtube.com/{VideoID}.json"): Dump = ReadJSON(f"Data/Storage/youtube.com/{VideoID}.json")["dump"]

		# Если ссылка относится к TikTok.
		if "tiktok.com" in link:
			# Парсинг ссылки.
			VideoID = link.split("?")[0].split("/")[-1]
			# Если локальное описание существует, подгрузить его.
			if os.path.exists(f"Data/Storage/tiktok.com/{VideoID}.json"): Dump = ReadJSON(f"Data/Storage/tiktok.com/{VideoID}.json")["dump"]

		return Dump

	def __PrettyFormatName(self, name: str) -> str:
		"""
		Делает название формата более привлекательным и округляет.
			name – название формата.
		"""

		# Список поддерживаемых разрешений видео.
		SupportedResolutions = [144, 240, 360, 480, 720, 1080, 2560, 3840]

		# Если название не определяет только аудио.
		if name != "audio only":
			# Получение ширины кадра.
			Width = int(name.split("x")[0])
			# Округление разрешения до ближайшего поддерживаемого.
			Width = min(SupportedResolutions, key = lambda SupportedResolution: abs(SupportedResolution - Width))
			# Форматирование названия.
			if Width == 2560: name = "2K"
			elif Width == 3840: name = "4K"
			else: name = f"{Width}p"

		else:
			# Обнуление названия.
			name = None

		return name

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, lib_path: str | None = None, proxy: str | None = None):
		"""
		Абстракция управления библиотекой yt-dlp.
			lib_path – путь к исполняемому файлу библиотеки;
			proxy – данные прокси-сервера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Путь к исполняемому файлу библиотеки.
		self.__LibPath = lib_path or "yt-dlp"
		# Ключ данных прокси.
		self.__Proxy = f"--proxy {proxy}" if proxy else ""
	
	def download_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		# Состояние: успешна ли загрузка.
		IsSuccess = False
		# Проверка и создание директории.
		if not os.path.exists(directory): os.makedirs(directory)
		
		try:
			# Составление команды.
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" {self.__Proxy} -o {directory}{filename} --extract-audio --recode m4a"
			# Если скачивание успешно, переключить статус.
			if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		return IsSuccess
	
	def download_video(self, link: str, directory: str, filename: str, format_id: str) -> bool:
		"""
		Скачивает видео.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""
		
		# Состояние: успешна ли загрузка.
		IsSuccess = False
		# Проверка и создание директории.
		if not os.path.exists(directory): os.makedirs(directory)
		
		try:
			# Составление команды.
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}+bestaudio/best --recode mp4 {self.__Proxy}  -o {directory}{filename}"
			# Если скачивание успешно, переключить статус.
			if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		return IsSuccess

	def get_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		# Информация о видео.
		Info = None
		
		try:
			# Составление команды.
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy}",
			# Получение дампа с информацией о видео.
			Dump = subprocess.getoutput(Command)
			# Если нет ошибки дампирования, спарсить дамп в словарь.
			if not Dump.startswith("ERROR"): Info = json.loads(Dump)
			# Фильтрация форматов.
			Info = self.__FilterInfo(Info)
	
		except Exception as ExceptionData: print(ExceptionData)
		
		return Info

	def get_resolutions(self, info: dict, pretty: bool = True) -> dict:
		"""
		Возвращает словарь определений разрешений, где клюём является ширина кадра, а значением – ID формата.
			info – словарное представления описания видео;
			pretty – указывает, нужно ли преобразовывать словарь разрешений в красивый вид.
		"""

		# Словарь разрешений.
		Resolutions = dict()

		# Для каждого формата.
		for Format in info["formats"]:

			# Если формат ещё не записан и валиден.
			if Format["resolution"] not in Resolutions.values() and Format["resolution"]:
				# Получение названия формата. .split("x")[0]
				Name = Format["resolution"]
				# Если указано, сделать название формата привлекательным.
				if pretty: Name = self.__PrettyFormatName(Name)
				# Если формат не является звуковым, записать его.
				if Name != None: Resolutions[Name] = Format["format_id"]

		return Resolutions