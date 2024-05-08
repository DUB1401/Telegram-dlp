from dublib.Methods import RemoveFolderContent, WriteJSON

import subprocess
import json
import sys
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __FilterDump(self, dump: dict) -> dict:
		"""Фильтрует только видео MP4 в дампе описания."""

		# Буфер обработки.
		Buffer = dump.copy()
		# Очистка форматов.
		Buffer["formats"] = list()
		
		# Для каждого формата.
		for Format in dump["formats"]:
			# Если формат упакован в MP4 и содержит аудиодорожку.
			#if "vcodec" in Format.keys() and Format["vcodec"] != "none" and "acodec" in Format.keys() and Format["acodec"] != "none": Buffer["formats"].append(Format)
			if Format["ext"] == "mp4": Buffer["formats"].append(Format)

		return Buffer

	def __NormalizeDirectory(self, path: str):
		"""
		Приводит к стандартному для ОС виду путь к каталогу.
			dir – путь к каталогу.
		"""

		# Если запуск на платформе Linux.
		if "linux" in sys.platform:
			# Реверс типа косых черт.
			path = path.replace("\\", "/")
			# Удаление конечной черты (позволяет указывать или не указывать данный символ).
			path = path.rstrip("/")
			# Добавление конечной черты.
			path = path + "/"
		
		else:
			# Реверс типа косых черт.
			path = path.replace("/", "\\")
			# Удаление конечной черты (позволяет указывать или не указывать данный символ).
			path = path.rstrip("\\")
			# Добавление конечной черты.
			path = path + "\\"

		# Если каталог не существует, создать.
		if not os.path.exists(path): os.makedirs(path)

		return path

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, lib_dir: str = "", proxy: str | None = None):
		"""Абстракция управления библиотекой yt-dlp."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Каталог с библиотекой.
		self.__LibDirectory = self.__NormalizeDirectory(lib_dir)
		# Ключ с прокси.
		self.__Proxy = f"--proxy {proxy}" if proxy else ""
	
	def download_audio(self, link: str, save_dir: str, filename: str) -> bool:
		"""Скачивает аудиодорожку."""

		# Состояние: успешна ли загрузка.
		IsSuccess = False
		# Нормализация каталога для ОС.
		save_dir = self.__NormalizeDirectory(save_dir)
		# Очистка целевой директории.
		RemoveFolderContent(save_dir)
		# Определения исполняемых команд.
		Commands = {
			 "linux": "python3." + str(sys.version_info[1]) +  f" yt-dlp/yt-dlp \"{link}\" -f 140 --audio-format mp3 {self.__Proxy} -o {save_dir}{filename}.mp3",
			 "win32": f"yt-dlp\\yt-dlp.exe {link} -f 140 --audio-format mp3 {self.__Proxy} -o {save_dir}{filename}.mp3"
		}
		
		try:
			# Если скачивание успешно, переключить статус.
			if os.system(Commands[sys.platform]) == 0: IsSuccess = True

		except: pass
		
		return IsSuccess

	def download_video(self, link: str, save_dir: str, filename: str, format_id: str) -> bool:
		"""Скачивает видео."""

		# Состояние: успешна ли загрузка.
		IsSuccess = False
		# Нормализация каталога для ОС.
		save_dir = self.__NormalizeDirectory(save_dir)
		# Очистка целевой директории.
		RemoveFolderContent(save_dir)
		# Определения исполняемых команд.
		Commands = {
			 "linux": "python3." + str(sys.version_info[1]) +  f" yt-dlp/yt-dlp \"{link}\" --format {format_id}+bestaudio --recode mp4 {self.__Proxy} -o {save_dir}{filename}.mp4",
			 "win32": f"yt-dlp\\yt-dlp.exe {link} --format {format_id}+bestaudio --recode mp4 {self.__Proxy} -o {save_dir}{filename}.mp4"
		}
		
		try:
			# Если скачивание успешно, переключить статус.
			if os.system(Commands[sys.platform]) == 0: IsSuccess = True

			# Если скачивание неуспешно.
			if not IsSuccess: 
				# Если скачивание без фильтра аудио успешно, переключить статус.
				if os.system(Commands[sys.platform].replace("+bestaudio", "")) == 0: IsSuccess = True

		except: pass
		
		return IsSuccess

	def get_info(self, link: str, file: str | None = None) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на страницу с видео;
			file – имя файла, в который будет записан результат.
		"""

		# Описание.
		Dump = None
		# Определения исполняемых команд.
		Commands = {
			 "linux": "python3." + str(sys.version_info[1]) +  f" {self.__LibDirectory}yt-dlp \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy}",
			 "win32": f"{self.__LibDirectory}yt-dlp.exe {link} --dump-json --quiet --no-warnings --skip-download {self.__Proxy}"
		}
		# Получение дампа с информацией о видео.
		Dump = subprocess.getoutput(Commands[sys.platform])
		
		#try:
		# Если нет ошибки дампирования, спарсить дамп в словарь.
		if not Dump.startswith("ERROR"): Dump = json.loads(Dump)
		# Фильтрация форматов.
		Dump = self.__FilterDump(Dump)
		# Запись результата в файл.
		if file: WriteJSON(file, Dump)
		
		#except: pass
		
		return Dump
	
	def get_resolutions(self, dump: dict) -> dict:
		"""
		Возвращает словарь определений разрешений, где клюём является разрешение, а значением – ID формата.
			dump – словарное представления описания видео.
		"""

		# Словарь разрешений.
		Resolutions = dict()

		# Для каждого формата.
		for Format in dump["formats"]:
			# Если формат ещё не записан, записать его.
			if Format["resolution"] not in Resolutions.values(): Resolutions[Format["resolution"]] = Format["format_id"]

		return Resolutions