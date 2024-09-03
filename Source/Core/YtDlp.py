from Source.Core.Storage import Storage

import subprocess
import json
import sys
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckWatermark(self, domain: str, format: dict) -> bool:
		"""
		Проверяет, содержит ли формат водяной знак.
			domain – домен сайта-источника;
			format – формат.
		"""

		IsWatermarked = False

		if domain == "tiktok.com":

			if format["format_id"] == "download": IsWatermarked = True

		return IsWatermarked

	def __FilterInfo(self, info: dict) -> dict:
		"""
		Оставляет только основные форматы видео.
			info – словарь описания видео.
		"""

		Buffer = info.copy()
		Buffer["formats"] = list()
		
		for Format in info["formats"]:
			if Format["ext"] == "mp4": Buffer["formats"].append(Format)

		return Buffer

	def __PrettyFormatName(self, name: str, watermarked: bool = False) -> str:
		"""
		Делает название формата более привлекательным и округляет.
			name – название формата.
		"""

		SupportedResolutions = [144, 240, 360, 480, 720, 1080, 2560, 3840, 7680]

		if name not in ["audio only"]:

			if name and "x" in name:
				Width = int(name.split("x")[0].rstrip("p"))
				Width = min(SupportedResolutions, key = lambda SupportedResolution: abs(SupportedResolution - Width))
				if Width == 720: name = "HD"
				elif Width == 1080: name = "Full HD"
				elif Width == 2560: name = "2K"
				elif Width == 3840: name = "4K"
				elif Width == 7680: name = "8K"
				else: name = f"{Width}p"

			else: name = "null"

			if watermarked:
				name += "w"

			elif name == "null": name = None

		else:
			name = None

		return name

	def __SortResolutions(self, resolutions: dict) -> dict:
		"""
		Сортирует разрешения в определённом порядке.
			resolutions – словарь разрешений.
		"""
		
		Order = ["144p", "240p", "360p", "480p", "HD", "Full HD", "2K", "4K", "8K"]
		BaseResolutions = [Key for Key in resolutions if Key in Order]
		ExtraResolutions = [Key for Key in resolutions if Key not in Order]
		BaseResolutions = sorted(BaseResolutions, key = lambda Resolution: Order.index(Resolution))
		Resolutions = BaseResolutions + ExtraResolutions
		resolutions = {Key: resolutions[Key] for Key in Resolutions}
		
		return resolutions
	
	#==========================================================================================#
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ СКАЧИВАНИЯ АУДИО <<<<< #
	#==========================================================================================#

	def __instagram_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {directory}{filename} --extract-audio --recode m4a --cookies yt-dlp/instagram.cookies {self.__Proxy}"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __tiktok_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {directory}{filename} --extract-audio --recode m4a"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __youtube_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {directory}{filename} --extract-audio --recode m4a"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess

	#==========================================================================================#
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ СКАЧИВАНИЯ ВИДЕО <<<<< #
	#==========================================================================================#

	def __instagram_video(self, link: str, directory: str, filename: str, format_id: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}+bestaudio --recode mp4 -o {directory}{filename} --cookies yt-dlp/instagram.cookies"
		ExitCode = os.system(Command)
		if ExitCode in [0, 256]: IsSuccess = True

		return IsSuccess
	
	def __tiktok_video(self, link: str, directory: str, filename: str, format_id: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} --recode mp4 -o {directory}{filename}"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __youtube_video(self, link: str, directory: str, filename: str, format_id: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""

		IsSuccess = False
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}+bestaudio --recode mp4 -o {directory}{filename}"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess

	#==========================================================================================#
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ ПОЛУЧЕНИЯ ДАННЫХ <<<<< #
	#==========================================================================================#

	def __instagram_info(self, link: str) -> dict | None:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""

		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download --cookies yt-dlp/instagram.cookies",
		Dump = subprocess.getoutput(Command)
		Info = None 

		if not Dump.startswith("ERROR"):
			if "\n" in Dump: Dump = Dump.split("\n")[0]
			Info = json.loads(Dump)

		return Info

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage: Storage, lib_path: str | None = None, proxy: str | None = None):
		"""
		Абстракция управления библиотекой yt-dlp.
			storage – хранилище данных;\n
			lib_path – путь к исполняемому файлу библиотеки;\n
			proxy – данные прокси-сервера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__LibPath = lib_path or "yt-dlp"
		self.__Proxy = f"--proxy {proxy}" if proxy else ""
		self.__Storage = storage
	
	def download_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		if not os.path.exists(directory): os.makedirs(directory)
		Domain = self.__Storage.parse_site_name(link)
		IsSuccess = False

		try:

			if Domain == "instagram.com": IsSuccess = self.__instagram_audio(link, directory, filename)
			elif Domain == "tiktok.com": IsSuccess = self.__tiktok_audio(link, directory, filename)
			elif Domain == "youtube.com": IsSuccess = self.__youtube_audio(link, directory, filename)

			else:
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {directory}{filename} --extract-audio --recode m4a {self.__Proxy}"
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
		
		if not os.path.exists(directory): os.makedirs(directory)
		Domain = self.__Storage.parse_site_name(link)
		IsSuccess = False
		
		try:

			if Domain == "instagram.com": IsSuccess = self.__instagram_video(link, directory, filename, format_id)
			elif Domain == "tiktok.com": IsSuccess = self.__tiktok_video(link, directory, filename, format_id)
			elif Domain in ["youtube.com", "vk.com"]: IsSuccess = self.__youtube_video(link, directory, filename, format_id)

			else:
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} --recode mp4 -o {directory}{filename} {self.__Proxy}"
				if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		return IsSuccess

	def get_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Domain = self.__Storage.parse_site_name(link)
		Info = None
		
		try:

			if Domain == "instagram.com": Info = self.__instagram_info(link)

			else: 
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy}",
				Dump = subprocess.getoutput(Command)
				if not Dump.startswith("ERROR"): Info = json.loads(Dump)

			if Info: self.__FilterInfo(Info)
	
		except Exception as ExceptionData: print(ExceptionData)
		
		from dublib.Methods.JSON import WriteJSON
		WriteJSON("test.json", Info)

		return Info

	def get_resolutions(self, info: dict, pretty: bool = True) -> dict:
		"""
		Возвращает словарь определений разрешений, где клюём является ширина кадра, а значением – ID формата.
			info – словарное представления описания видео;
			pretty – указывает, нужно ли преобразовывать словарь разрешений в красивый вид.
		"""

		Resolutions = dict()

		for Format in info["formats"]:
			Watermarked = self.__CheckWatermark(info["webpage_url_domain"], Format)

			if Format["resolution"] or Watermarked:

				if Format["resolution"] not in Resolutions.values():
					Name = Format["resolution"]
					if pretty: Name = self.__PrettyFormatName(Name, Watermarked)
					if Name != None: Resolutions[Name] = Format["format_id"]

		Resolutions = self.__SortResolutions(Resolutions)

		return Resolutions